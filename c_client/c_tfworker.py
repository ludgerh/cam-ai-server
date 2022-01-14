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

from time import sleep, time
from collections import deque
from queue import Empty
from os import getpid
import numpy as np
import json
import cv2 as cv
from random import random
from multiprocessing import Process, Queue, shared_memory
from threading import Thread, Timer, Lock, get_ident
from logging import (getLogger, DEBUG, INFO, FileHandler as LogFileHandler, 
  StreamHandler as LogStreamHandler, Formatter)
from multitimer import MultiTimer
from traceback import format_exc
from django.db.utils import OperationalError
from .models import school
from .l_tools import logdict
from .c_tools import djconf, classes_list, cmetrics, hit100
from .c_base import c_base
if ((djconf.getconfigfloat('gpu_sim') < 0) 
    and (not djconf.getconfig('tfw_wsurl',''))):
  from os import environ
  environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
  environ["CUDA_VISIBLE_DEVICES"]="0"
  from tensorflow.keras.models import load_model
if djconf.getconfig('tfw_wsurl',''):
  from websocket import WebSocket #, enableTrace
  #enableTrace(True)

#***************************************************************************
#
# tools common
#
#***************************************************************************

class QueueUnknownKeyword(Exception):
  def __init__(self, keyword, message="Unknown keyword: "):
    self.message = message + keyword
    super().__init__(self.message)

#***************************************************************************
#
# tools server
#
#***************************************************************************

class model_buffer(deque):

  def __init__(self, schoolnr, xdim, ydim):
    super().__init__()
    self.ts = time()
    self.nr_images = 0
    self.img_rest = np.empty((0, xdim, ydim, 3), np.uint8)
    self.fra_in_rest = []
    self.event_id_rest = []
    self.pre_rest = None
    self.fra_out_rest = None
    self.event_out_rest = None
    self.BufferLock = Lock()

  def append(self, item):
    with self.BufferLock:
      # item[0] = model, item[1] = np.imagelist, item[2] = listofframenrs, 
      # item[3] = userindex, item[4] = eventid
      super().append(item)
      self.nr_images += item[1].shape[0]
    self.ts = time()

  def get(self, maxcount):
    with self.BufferLock:
      result = [self.img_rest, self.fra_in_rest, self.event_id_rest]
      if self.img_rest.shape[0] > 0:
        self.len_user = [(self.img_rest.shape[0], self.img_rest_user, True)]
      else:
        self.len_user = []
      while (len(self) > 0) and (result[0].shape[0] < maxcount):
        item = self.popleft()
        self.nr_images -= item[1].shape[0]
        finished = ((result[0].shape[0] + item[1].shape[0]) <= maxcount)
        self.len_user.append((item[1].shape[0], item[3], finished))
        result[0] = np.vstack((result[0], item[1]))
        result[1] += item[2]
        result[2] += [item[4]]
        self.img_rest_user = item[3]
      self.img_rest = result[0][maxcount:]
      self.fra_in_rest = result[1][maxcount:]
      self.event_id_rest = result[2][maxcount:]
    return([result[0][:maxcount], result[1][:maxcount], result[2][:maxcount], ])

class tf_user(object):

  def __init__(self, clientset, clientlock):
    self.clientset = clientset
    self.clientlock = clientlock
    with self.clientlock:
      i = 0
      while not (i in self.clientset):
        i += 1
      self.clientset.discard(i)
      self.id = i

  def __del__(self):
    with self.clientlock:
      self.clientset.add(self.id)

#***************************************************************************
#
# tools client
#
#***************************************************************************

#***************************************************************************
#
# tf_worker common
#
#***************************************************************************

class tf_worker(Process):

  def __init__(self, idx, nr_of_clients, modelcheck=()):
    super().__init__()
    self.id = idx
    self.is_ready = False
    self.users = {}
    self.model_buffers = {}
    self.gpu_sim = djconf.getconfigfloat('gpu_sim', -1)
    self.gpu_sim_loading = djconf.getconfigint('gpu_sim_loading', 0)
    if self.gpu_sim >= 0:
      self.cachedict = {}
    self.tfw_wsurl = djconf.getconfig('tfw_wsurl','')
    self.tfw_wsname = djconf.getconfig('tfw_wsname','')
    self.tfw_wspass = djconf.getconfig('tfw_wspass','')
    self.tfw_maxblock = djconf.getconfigint('tfw_maxblock', 8)
    self.tfw_timeout = djconf.getconfigfloat('tfw_timeout', 0.1)
    self.tfw_savestats = djconf.getconfigint('tfw_savestats', 0)
    self.tfw_max_nr_models = djconf.getconfigint('tfw_max_nr_models', 64)
    if self.tfw_wsurl:
      self.ws_ts = time()
      self.ws = WebSocket()
      self.ws.connect(self.tfw_wsurl)
      outdict = {
        'code' : 'auth',
        'name' : self.tfw_wsname,
        'pass' : self.tfw_wspass,
      }
      part1 = len(json.dumps(outdict).encode()).to_bytes(4, byteorder='big')
      part2 = json.dumps(outdict).encode()
      self.ws.send(part1 + part2, opcode=2)
      #MultiTimer(interval=20, function=self.send_ping, runonstart=False).start()
    self.modelcheck = modelcheck
    self.allmodels = {}
    self.activemodels = {}
    self.processlock = Lock()
    #*** Server Vars (not complete)
    self.nr_of_clients = nr_of_clients
    self.clientset = set(range(nr_of_clients))
    self.clientlock = Lock()
    #*** Client Vars (not complete)
    self.eventdicts = {}
    self.number_of_users = 0

  def send_ping(self):
    if (time() - self.ws_ts) > 15:
      outdict = {'code' : 'ping',}
      part1 = len(json.dumps(outdict).encode()).to_bytes(4, byteorder='big')
      part2 = json.dumps(outdict).encode()
      self.ws.send(part1 + part2, opcode=2)

#***************************************************************************
#
# tf_worker server
#
#***************************************************************************

  def process_buffer(self, schoolnr, logger, had_timeout=False):
    e_school = school.objects.get(id=schoolnr).e_school
    model_type = school.objects.get(id=schoolnr).model_type
    if (model_type == 'cam-ai_model') or (model_type == 'nasnetlarge'):
      normalizer = 255
    else:
      normalizer = None

    ts_one = time()
    self.model_buffers[schoolnr].ts = time()
    slice_to_process = self.model_buffers[schoolnr].get(self.tfw_maxblock)
    framelist = slice_to_process[1]
    eventlist = slice_to_process[2]
    self.check_model(schoolnr, logger)
    if self.gpu_sim >= 0: #GPU Simulation with random
      if self.gpu_sim > 0:
        sleep(self.gpu_sim)
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
    elif self.tfw_wsurl: #Predictions from Server
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
        self.ws.send(cv.imencode('.jpg', slice_to_process[0][i])[1].tobytes(), 
          opcode=2)
      predictions = np.array(json.loads(self.ws.recv()), dtype=np.float32)
    else: #local GPU
      if normalizer:
        slice_to_process[0] = np.float32(slice_to_process[0])/255
      if slice_to_process[0].shape[0] < self.tfw_maxblock:
        patch = np.zeros((self.tfw_maxblock - slice_to_process[0].shape[0], 
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
      subevents = eventlist[:item[0]]
      predictions = predictions[item[0]:]
      framelist = framelist[item[0]:]
      eventlist = eventlist[item[0]:]
      if item[2]:
        if self.model_buffers[schoolnr].pre_rest is not None:
          subslice = np.vstack((self.model_buffers[schoolnr].pre_rest, 
            subslice))
          subframes = self.model_buffers[schoolnr].fra_out_rest + subframes
          subevents = self.model_buffers[schoolnr].event_out_rest + subevents
          self.model_buffers[schoolnr].pre_rest = None
          self.model_buffers[schoolnr].fra_out_rest = None
          self.model_buffers[schoolnr].event_out_rest = None
        if item[1] in self.users:
          self.outqueues[item[1]].put(('predictions', subslice, subframes, subevents, item[1]))
      else:
        self.model_buffers[schoolnr].pre_rest = subslice
        self.model_buffers[schoolnr].fra_out_rest = subframes
        self.model_buffers[schoolnr].event_out_rest = subevents
    if self.tfw_savestats > 0: #Later to be written in DB
      newtime = time()
      logtext = 'School: ' + str(schoolnr).zfill(3)
      logtext += ('  Buffer Size: ' 
        + str(self.model_buffers[schoolnr].nr_images).zfill(5))
      logtext += ('  Proc Time: ' 
        + str(round(newtime - ts_one, 3)).ljust(5, '0'))
      if had_timeout:
        logtext += ' T'
      logger.info(logtext)

  def in_reader_proc(self, logger): #called by host (c_tf_worker)
    try:
      while True:
        received = self.inqueue.get()
        #print('In:', received)
        if (received[0] == 'done'):
          break
        elif (received[0] == 'unregister'):
          if received[1] in self.users:
            del self.users[received[1]]
        elif (received[0] == 'get_is_ready'):
          self.outqueues[received[1]].put(('put_is_ready', self.is_ready))
        elif (received[0] == 'get_xy'):
          self.check_model(received[1], logger)
          xdim = self.allmodels[received[1]]['xdim']
          ydim = self.allmodels[received[1]]['ydim']
          self.outqueues[received[2]].put(('put_xy', (xdim, ydim)))
        elif (received[0] == 'imglist'):
          schoolnr = received[1]
          if schoolnr not in self.model_buffers:
            self.check_model(schoolnr, logger)
            self.model_buffers[schoolnr] = model_buffer(schoolnr, 
              self.allmodels[schoolnr]['xdim'], 
              self.allmodels[schoolnr]['ydim'])
          self.model_buffers[schoolnr].append(received[1:])
          while self.model_buffers[schoolnr].nr_images >= self.tfw_maxblock:
            with self.processlock:
              self.process_buffer(schoolnr, logger)
        else:
          raise QueueUnknownKeyword(received[0])
    except:
      logger.error(format_exc())
      logger.handlers.clear()

  def sh_checker_proc(self, logger): #called by host (c_tf_worker)
    try:
      while True:
        sleep(0.1)
        if (self.sharelist[1] != -1) and (self.sharelist[0] != -1):
          self.sharelist[0] = -1
          myuser = tf_user(self.clientset, self.clientlock)
          self.users[myuser.id] = myuser
          self.sharelist[2] = myuser.id
    except:
      logger.error(format_exc())
      logger.handlers.clear()

  def run(self):
    logname = 'tf_worker_'+str(self.id)
    self.logger = getLogger(logname)
    self.logger.setLevel(DEBUG)
    fh = LogFileHandler(djconf.getconfig('logdir')+logname+'.log')
    fh.setLevel(logdict[djconf.getconfig('loglevel','INFO')])
    ch = LogStreamHandler()
    ch.setLevel(logdict[djconf.getconfig('loglevel','INFO')])
    formatter = Formatter("{asctime} [{levelname:8}] {message}",
      "%d.%m.%Y %H:%M:%S","{")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    self.logger.addHandler(ch)
    self.logger.addHandler(fh)
    self.logger.info('Started Process '+str(logname)+'...')
    #[process_id, thread_id, tf_w_index]
    self.sharelist = shared_memory.ShareableList([-1, -1, -1], name='tfworker'+str(self.id)) 
    in_reader_p = Thread(target=self.in_reader_proc, args = (self.logger, ))
    in_reader_p.start()
    sh_checker_p = Thread(target=self.sh_checker_proc, args = (self.logger, ))
    sh_checker_p.start()
    try:
      for schoolnr in self.modelcheck:
        self.check_model(schoolnr, self.logger, test_pred = True)
      self.logger.info('***** All Models are ready.')
      self.is_ready = True
      schoolnr = -1
      while len(self.model_buffers) == 0:
        sleep(djconf.getconfigfloat('long_brake', 1.0))
      while True:
        while True:
          schoolnr += 1
          if schoolnr > max(self.model_buffers):
            schoolnr = 1
          if schoolnr in self.model_buffers:
            break
        with self.processlock:
          do_run = (
            ((self.model_buffers[schoolnr].ts + self.tfw_timeout) < time()) 
            and (self.model_buffers[schoolnr].nr_images > 0))
          if do_run:
            self.process_buffer(schoolnr, self.logger, had_timeout=True)
        if not do_run:
          sleep(djconf.getconfigfloat('short_brake', 0.01))
    except:
      self.sharelist.shm.close()
      self.sharelist.shm.unlink()
      self.logger.error(format_exc())
      self.logger.handlers.clear()
    self.logger.info('Finished Process '+str(logname)+'...')
    self.logger.handlers.clear()

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
      if not (schoolnr in self.allmodels):
        self.allmodels[schoolnr] = {}
        self.allmodels[schoolnr]['time'] = myschool.lastfile
        if self.gpu_sim >= 0:
          self.allmodels[schoolnr]['xdim'] = 50
          self.allmodels[schoolnr]['ydim'] = 50
          sleep(self.gpu_sim_loading) 
        elif self.tfw_wsurl:
          self.allmodels[schoolnr]['xdim'] = djconf.getconfigint('xdim')
          self.allmodels[schoolnr]['ydim'] = djconf.getconfigint('ydim')
          sleep(self.gpu_sim_loading) 
        else:
          tempmodel= load_model(myschool.dir+'model/'+myschool.model_type+'.h5', 
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
        logger.info('***** Got model file #'+str(schoolnr) 
          + ', type: '+myschool.model_type)
      if (self.gpu_sim >= 0) or self.tfw_wsurl:
        sleep(self.gpu_sim_loading / 2)
        self.activemodels[schoolnr] = True
      else:
        if len(self.activemodels) < self.tfw_max_nr_models:
          if tempmodel is None:
            self.activemodels[schoolnr] = load_model(myschool.dir 
              + 'model/'+myschool.model_type+'.h5', 
              custom_objects={'cmetrics': cmetrics, 'hit100': hit100,})
          else:
            self.activemodels[schoolnr] = tempmodel
        else: #this is not tested, needed if # of models > self.max_nr_models
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
            self.activemodels[schoolnr] = load_model(myschool.dir
              + 'model/'+myschool.model_type+'.h5', 
              custom_objects={'cmetrics': cmetrics, 'hit100': hit100,})
          del self.activemodels[nr_to_replace]
      logger.info('***** Got model buffer #'+str(schoolnr)+', type: '
        + myschool.model_type)
    if test_pred:
      if (self.gpu_sim < 0) and (not self.tfw_wsurl):
        xdata = np.random.rand(8,self.allmodels[schoolnr]['xdim'],
          self.allmodels[schoolnr]['ydim'],3)
        self.activemodels[schoolnr].predict_on_batch(xdata)
      else:
        sleep(self.gpu_sim_loading / 3)
      logger.info('***** Testrun for model #' + str(schoolnr)+', type: '
        + myschool.model_type)

#***************************************************************************
#
# tf_worker client
#
#***************************************************************************

  def out_reader_proc(self, index): #called by client (c_eventer)
    #print('Started Outqueue', index)
    while (received := self.outqueues[index].get())[0] != 'done':
      #print('Out:', received)
      if (received[0] == 'put_is_ready'):
        self.is_ready = received[1]
      elif (received[0] == 'put_xy'):
        self.xy = received[1]
      elif (received[0] == 'predictions'):
        #print(received[4])
        if (received[4] in self.eventdicts) and (received[3][0] in self.eventdicts[received[4]]):
          self.eventdicts[received[4]][received[3][0]].set_pred(received[2], received[1])
      else:
        raise QueueUnknownKeyword(received[0])
    #print('Stopped Outqueue', received)

  def register(self, eventdict):
    self.number_of_users += 1
    self.sharelist = shared_memory.ShareableList(name='tfworker'+str(self.id))
    while self.sharelist[1] != -1:
      sleep(djconf.getconfigfloat('short_brake', 0.01))
    self.sharelist[0] = getpid()
    self.sharelist[1] = get_ident()
    while self.sharelist[2] == -1:
      sleep(djconf.getconfigfloat('short_brake', 0.01))
    self.tf_w_index = self.sharelist[2]
    self.eventdicts[self.tf_w_index] = eventdict
    self.sharelist[0] = -1
    self.sharelist[2] = -1
    self.sharelist[1] = -1
    return(self.tf_w_index)

  def run_out(self, id, index):
    self.id = id
    out_reader_p = Thread(target=self.out_reader_proc, args = (index, ))
    out_reader_p.start()
    
    #self.eventdicts[self.tf_w_index] = eventdict
    return(self.tf_w_index)

  def unregister(self, index):
    del self.eventdicts[index]
    self.inqueue.put(('unregister', index))
    self.number_of_users -= 1

  def check_ready(self, index):
    if not self.is_ready:
      self.is_ready = None
      self.inqueue.put(('get_is_ready', index))
      while self.is_ready is None:
        sleep(djconf.getconfigfloat('very_short_brake', 0.001))
    return(self.is_ready)

  def get_xy(self, school, index):
    self.xy = None
    self.inqueue.put(('get_xy', school, index))
    while self.xy is None:
      sleep(djconf.getconfigfloat('very_short_brake', 0.001))
    return(self.xy)
