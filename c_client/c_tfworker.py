# Copyright (C) 2021 Ludger Hellerhoff, ludger@booker-hellerhoff.de
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


import cv2 as cv
from queue import Queue, Empty
from threading import Lock, Timer
import numpy as np
from random import random
from time import sleep, time
from collections import deque
import json
import zlib
from multitimer import MultiTimer
from django.db.utils import OperationalError
from django.db import connection
from .models import school, eventer
from .c_tools import djconf, classes_list, cmetrics, hit100
if ((djconf.getconfigfloat('gpu_sim') < 0) 
    and (not djconf.getconfig('tfw_wsurl',''))):
  from os import environ
  environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
  environ["CUDA_VISIBLE_DEVICES"]="0"
  from tensorflow.keras.models import load_model
if djconf.getconfig('tfw_wsurl',''):
  from websocket import WebSocket#, enableTrace

gpu_sim = djconf.getconfigfloat('gpu_sim')
tfw_savestats = djconf.getconfigint('tfw_savestats', 0)
tfw_maxblock = djconf.getconfigint('tfw_maxblock', 8)
tfw_timeout = djconf.getconfigfloat('tfw_timeout', 1.0)
tfw_wsurl = djconf.getconfig('tfw_wsurl','')
tfw_wsname = djconf.getconfig('tfw_wsname','')
tfw_wspass = djconf.getconfig('tfw_wspass','')
if (gpu_sim < 0) and (not tfw_wsurl):
  gpu_sim_loading = 0
else:
  gpu_sim_loading = djconf.getconfigint('gpu_sim_loading', 0)

class model_buffer(deque):

  def __init__(self, schoolnr):
    super().__init__()
    self.ts = time()
    self.nr_images = 0
    self.img_rest = np.empty((0, 
      tfworker.allmodels[schoolnr]['xdim'], 
      tfworker.allmodels[schoolnr]['ydim'], 3), np.uint8)
    self.fra_in_rest = []
    self.pre_rest = None
    self.fra_out_rest = None

  def append(self, item):
    # item[0] = model, item[1] = (np.imagelist, listofframnrs), item[2] = userindex
    super().append(item)
    self.nr_images += item[1][0].shape[0]
    self.ts = time()

  def get(self, maxcount):
    result = [self.img_rest, self.fra_in_rest]
    if self.img_rest.shape[0] > 0:
      self.len_user = [(self.img_rest.shape[0], self.img_rest_user, True)]
    else:
      self.len_user = []
    while (len(self) > 0) and (result[0].shape[0] < maxcount):
      item = self.popleft()
      self.nr_images -= item[1][0].shape[0]
      finished = ((result[0].shape[0] + item[1][0].shape[0]) <= maxcount)
      self.len_user.append((item[1][0].shape[0], item[2], finished))
      result[0] = np.vstack((result[0], item[1][0]))
      result[1] += item[1][1]
      self.img_rest = result[0][maxcount:]
      self.fra_in_rest = result[1][maxcount:]
      self.img_rest_user = item[2]
      result[0] = result[0][:maxcount]
      result[1] = result[1][:maxcount]
    return(result)

class tf_user(object):

  clientset = set()

  def __init__(self):
    i = 0
    while i in tf_user.clientset:
      i += 1
    tf_user.clientset.add(i)
    self.id = i
    self.fifoin = Queue()
    self.fifoout = Queue()

  def fifoin_put(self, data):
    if (self.fifoin.qsize() < 10) and (self.fifoout.qsize() < 10):
      if type(data[1]) == np.ndarray:
        data[1] = (data[1], list(range(data[1].shape[0])))
      self.fifoin.put(data)

  def fifoin_get(self, **kwargs):
    return(self.fifoin.get(**kwargs))

  def fifoout_put(self, data):
    self.fifoout.put(data)

  def fifoout_get(self, **kwargs):
    return(self.fifoout.get(**kwargs))

  def __del__(self):
    tf_user.clientset.discard(self.id)

class c_tfworker:

  def __init__(self, max_nr_models=64):
    self.is_ready = False
    self.logger = None
    self.users = {}
    self.users_lock = Lock()
    self.model_buffers = {}
    self.max_nr_models = max_nr_models
    self.allmodels = {}
    self.activemodels = {}
    if tfw_savestats > 0:
      self.ts_rounds = {}
    if gpu_sim >= 0:
      self.cachedict = {}
    if tfw_wsurl:
      self.ws_ts = time()
      self.ws = WebSocket()
      #enableTrace(True)
      self.ws.connect(tfw_wsurl)
      outdict = {
        'code' : 'auth',
        'name' : tfw_wsname,
        'pass' : tfw_wspass,
      }
      part1 = len(json.dumps(outdict).encode()).to_bytes(4, byteorder='big')
      part2 = json.dumps(outdict).encode()
      self.ws.send(part1 + part2, opcode=2)
      MultiTimer(interval=20, function=self.send_ping, runonstart=False).start()
      #ws.close()
    # Debug - Stuff *****
    self.run1_count = 0
    self.run2_count = 0
    # *****

  def send_ping(self):
    if (time() - self.ws_ts) > 15:
      outdict = {'code' : 'ping',}
      part1 = len(json.dumps(outdict).encode()).to_bytes(4, byteorder='big')
      part2 = json.dumps(outdict).encode()
      self.ws.send(part1 + part2, opcode=2)

  def check_model(self, schoolnr, logger, test_pred = False):
    while True:
      try:
        myschool = school.objects.get(id=schoolnr)
        break
      except OperationalError:
        connection.close()
    if schoolnr in self.allmodels:
      if ((myschool.lastfile is not None)
          and	((self.allmodels[schoolnr]['time'] is None)
          or (myschool.lastfile > self.allmodels[schoolnr]['time']))):
        del self.allmodels[schoolnr]
        del self.activemodels[schoolnr]
    if not (schoolnr in self.activemodels):
      tempmodel = None
      if not (schoolnr in self.allmodels):
        self.allmodels[schoolnr] = {}
        self.allmodels[schoolnr]['time'] = myschool.lastfile
        if gpu_sim >= 0:
          self.allmodels[schoolnr]['xdim'] = 50
          self.allmodels[schoolnr]['ydim'] = 50
          sleep(gpu_sim_loading) 
        elif tfw_wsurl:
          self.allmodels[schoolnr]['xdim'] = djconf.getconfigint('xdim')
          self.allmodels[schoolnr]['ydim'] = djconf.getconfigint('ydim')
          sleep(gpu_sim_loading) 
        else:
          tempmodel = load_model(myschool.dir+'model/'+myschool.model_type+'.h5', 
            custom_objects={'cmetrics': cmetrics, 'hit100': hit100,})
          self.allmodels[schoolnr]['type'] = myschool.model_type
          self.allmodels[schoolnr]['xdim'] = tempmodel.layers[0].input_shape[1]
          self.allmodels[schoolnr]['ydim'] = tempmodel.layers[0].input_shape[2]
          self.allmodels[schoolnr]['weights'] = []
          self.allmodels[schoolnr]['weights'].append(
            tempmodel.get_layer(index=2).get_weights())
          self.allmodels[schoolnr]['weights'].append(
            tempmodel.get_layer(index=3).get_weights())
          self.allmodels[schoolnr]['weights'].append(
            tempmodel.get_layer(index=4).get_weights())
        logger.info('***** Got model file #'+str(schoolnr)+', type: '+myschool.model_type)
      if gpu_sim >= 0 or tfw_wsurl:
        sleep(gpu_sim_loading / 2)
        self.activemodels[schoolnr] = True
      else:
        if len(self.activemodels) < self.max_nr_models:
          if tempmodel is None:
            self.activemodels[schoolnr] = load_model(myschool.dir+'model/'+myschool.model_type+'.h5', 
              custom_objects={'cmetrics': cmetrics, 'hit100': hit100,})
          else:
            self.activemodels[schoolnr] = tempmodel
        else: #this case is not tested, needed if # of models > self.max_nr_models
          nr_to_replace = min(self.activemodels, 
            key= lambda x: self.activemodels[x]['time'])	
          if self.allmodels[nr_to_replace]['type'] == myschool.model_type:
            self.activemodels[schoolnr] = self.activemodels[nr_to_replace]
            self.activemodels[schoolnr].get_layer(index=2).set_weights(
              self.allmodels[schoolnr]['weights'][0])
            self.activemodels[schoolnr].get_layer(index=3).set_weights(
              self.allmodels[schoolnr]['weights'][1])
            self.activemodels[schoolnr].get_layer(index=4).set_weights(
              self.allmodels[schoolnr]['weights'][2])
          else:
            self.activemodels[schoolnr] = load_model(myschool.dir+'model/'+myschool.model_type+'.h5', 
              custom_objects={'cmetrics': cmetrics, 'hit100': hit100,})
          del self.activemodels[nr_to_replace]
      logger.info('***** Got model buffer #'+str(schoolnr)+', type: '+myschool.model_type)
    if test_pred:
      if (gpu_sim < 0) and (not tfw_wsurl):
        xdata = np.random.rand(8,self.allmodels[schoolnr]['xdim'],self.allmodels[schoolnr]['ydim'],3)
        self.activemodels[schoolnr].predict_on_batch(xdata)
      else:
        sleep(gpu_sim_loading / 3)
      logger.info('***** Testrun for model #'+str(schoolnr)+', type: '+myschool.model_type)

  def run1(self, logger):
    schoolnr = -1
    while len(self.model_buffers) == 0:
      sleep(0.01)
    while True:
      schoolnr += 1
      while schoolnr not in self.model_buffers:
        schoolnr += 1
        if schoolnr > max(self.model_buffers):
          schoolnr = 0
      # Debug - Stuff *****
      #if schoolnr == 4:
      #  self.run1_count += 1
      #  logger.debug('+++ run1 '+str(self.run1_count))
      # *****
      e_school = school.objects.get(id=schoolnr).e_school
      while True:
        had_timeout = (self.model_buffers[schoolnr].ts + tfw_timeout) < time()
        if ((self.model_buffers[schoolnr].nr_images >= tfw_maxblock) 
            or (had_timeout and self.model_buffers[schoolnr].nr_images > 0)):
          ts_one = time()
          self.model_buffers[schoolnr].ts = time()
          slice_to_process = self.model_buffers[schoolnr].get(tfw_maxblock)
          framelist = slice_to_process[1]
          self.check_model(schoolnr, logger)
          if gpu_sim >= 0: #GPU Simulation with random
            if gpu_sim > 0:
              sleep(gpu_sim)
            predictions = np.empty((0, len(classes_list)), np.float32)
            for i in slice_to_process[0]:
              myindex = round(np.asscalar(np.sum(i)))
              if myindex in self.cachedict:
                line = self.cachedict[myindex]
              else:
                line = []
                for j in range(len(classes_list)):
                  line.append(random())
                line = np.array([np.float32(line)])
                self.cachedict[myindex] = line
              predictions = np.vstack((predictions, line))
          elif tfw_wsurl: #Predictions from Server
            outdict = {
              'code' : 'imgl',
              'scho' : e_school,
            }
            part2 = json.dumps(outdict).encode()
            part1 = len(part2).to_bytes(4, byteorder='big')
            part3 = slice_to_process[0].shape[0].to_bytes(4, byteorder='big')
            self.ws.send(part1 + part2 + part3, opcode=2)
            for i in range(slice_to_process[0].shape[0]):
              self.ws_ts = time()
              self.ws.send(cv.imencode('.jpg', slice_to_process[0][i])[1].tobytes(), opcode=2)
            predictions = json.loads(self.ws.recv())
          else: #local GPU
            slice_to_process[0] = np.float32(slice_to_process[0])/255
            if slice_to_process[0].shape[0] < tfw_maxblock:
              patch = np.zeros((tfw_maxblock - slice_to_process[0].shape[0], 
                slice_to_process[0].shape[1], 
                slice_to_process[0].shape[2], 
                slice_to_process[0].shape[3]), 
                np.float32)
              portion = np.vstack((slice_to_process[0], patch))
              predictions = (
                self.activemodels[schoolnr].predict_on_batch(portion))
              predictions = predictions[:slice_to_process[0].shape[0]]
            else:
              predictions = (
                self.activemodels[schoolnr].predict_on_batch(slice_to_process[0]))
          for item in self.model_buffers[schoolnr].len_user:
            subslice = predictions[:item[0]]
            subframes = framelist[:item[0]]
            predictions = predictions[item[0]:]
            framelist = framelist[item[0]:]
            if item[2]:
              if self.model_buffers[schoolnr].pre_rest is not None:
                subslice = np.vstack((self.model_buffers[schoolnr].pre_rest, 
                  subslice))
                subframes = self.model_buffers[schoolnr].fra_out_rest + subframes
                self.model_buffers[schoolnr].pre_rest = None
                self.model_buffers[schoolnr].fra_out_rest = None
              with self.users_lock:
                if item[1] in self.users:
                  self.users[item[1]].fifoout_put((subslice, subframes))
            else:
              self.model_buffers[schoolnr].pre_rest = subslice
              self.model_buffers[schoolnr].fra_out_rest = subframes

          if tfw_savestats > 0: #Later to be written in DB
            newtime = time()
            logtext = 'School: ' + str(schoolnr).zfill(3)
            logtext += ('  Buffer Size: ' 
              + str(self.model_buffers[schoolnr].nr_images).zfill(5))
            logtext += ('  Proc Time: ' 
              + str(round(newtime - ts_one, 3)).ljust(5, '0'))
            if had_timeout:
              logtext += ' T'
            logger.info(logtext)

        else:
          sleep(0.01)
          break
      # Debug - Stuff *****
      #if schoolnr == 4:
      #  self.run1_count -= 1
      #  logger.debug('--- run1 '+str(self.run1_count))
      # *****

  def run2(self, logger):
    self.logger = logger
    used_models = []
    myeventers = eventer.objects.filter(active=True)
    for item in myeventers:
      if item.school not in used_models:
        used_models.append(item.school)
    for item in used_models:
      self.check_model(item, logger, test_pred = True)
    logger.info('***** All Models are ready.')
    self.is_ready = True
    userindex = -1
    while True:
      if len(self.users) == 0:
        sleep(0.01)
      else:
        userindex += 1
        while userindex not in self.users:
          userindex += 1
          if userindex > max(self.users):
            userindex = 0
        while True:
          try:
            newitem = self.users[userindex].fifoin_get(block=False)
            break
          except Empty:
            newitem = None
            break
        if newitem is None:
          sleep(0.01)
        else:
          # Debug - Stuff *****
          #if newitem[0] == 4:
          #  self.run2_count += 1
          #  logger.debug('++++++ run2 '+str(self.run2_count))
          # *****
          schoolnr = newitem[0]
          newitem.append(userindex)
          if schoolnr not in self.model_buffers:
            self.model_buffers[schoolnr] = model_buffer(schoolnr)
          self.model_buffers[schoolnr].append(newitem)
          #print('model_buffer', len(self.model_buffers[schoolnr]))
          # Debug - Stuff *****
          #if newitem[0] == 4:
          #  self.run2_count -= 1
          #  logger.debug('----- run2 '+str(self.run2_count))
          # *****

  def register(self):
    with self.users_lock:
      myuser = tf_user()
      self.users[myuser.id] = myuser
    #if self.logger:
    #  self.logger.info('Registered client #'+str(myuser.id)+' >'+str(len(self.users.keys())))
    return(myuser.id)

  def do_unregister(self, index):
    with self.users_lock:
      if index in self.users:
        del self.users[index]
    #if self.logger:
    #  self.logger.info('Unregistered client #'+str(index)+' >'+str(len(self.users.keys())))
    #  self.logger.info(str(self.users.keys()))

  def unregister(self, index):
    Timer(60, self.do_unregister, [index]).start()

tfworker = c_tfworker(
  djconf.getconfigint('max_nr_models', 64),
)


