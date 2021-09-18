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
  import tensorflow as tf
  from tensorflow.keras.models import load_model, Sequential
  from tensorflow.keras.layers import Flatten, Dense
  from tensorflow.keras.optimizers import Adam
  from tensorflow.keras.regularizers import l2
  from tensorflow.keras.constraints import max_norm
if djconf.getconfig('tfw_wsurl',''):
  from websocket import WebSocket

gpu_sim = djconf.getconfigfloat('gpu_sim')
tfw_savestats = djconf.getconfigint('tfw_savestats', 0)
tfw_maxblock = djconf.getconfigint('tfw_maxblock', 8)
tfw_timeout = djconf.getconfigfloat('tfw_timeout', 1.0)
tfw_wsurl = djconf.getconfig('tfw_wsurl','')
tfw_wsname = djconf.getconfig('tfw_wsname','')
tfw_wspass = djconf.getconfig('tfw_wspass','')
xdim = djconf.getconfigint('xdim', 331)
ydim = djconf.getconfigint('ydim', 331)
if (gpu_sim < 0) and (not tfw_wsurl):
  l_rate = djconf.getconfigfloat('learning_rate', 0.0001)
  weight_decay = djconf.getconfigfloat('weight_decay', None)
  weight_constraint = djconf.getconfigfloat('weight_constraint', None)
  dropout = djconf.getconfigfloat('dropout', None)
  base_model = load_model(djconf.getconfig('basemodelpath')+'basemodel.h5')
  base_model.trainable = False

  if weight_decay is None:
	  decay_reg = None
  else:
	  decay_reg = l2(weight_decay)
  if weight_constraint is None:
	  weight_norm = None
  else:
	  weight_norm = max_norm(weight_constraint)
  gpu_sim_loading = 0
else:
  gpu_sim_loading = djconf.getconfigint('gpu_sim_loading', 0)

def makemodel():
  model = Sequential()
  model.add(base_model)
  model.add(Flatten())
  model.add(Dense(128,activation="relu", 
    kernel_regularizer=decay_reg, bias_regularizer=decay_reg, 
    kernel_constraint=weight_norm, bias_constraint=weight_norm))
  if dropout is not None:
    model.add(Dropout(dropout))
  model.add(Dense(64,activation="relu", 
    kernel_regularizer=decay_reg, bias_regularizer=decay_reg, 
    kernel_constraint=weight_norm, bias_constraint=weight_norm))
  if dropout is not None:
    model.add(Dropout(dropout))
  model.add(Dense(len(classes_list), activation='sigmoid'))
  model.compile(loss='binary_crossentropy',
    optimizer=Adam(learning_rate=l_rate),
    metrics=[hit100, cmetrics])
  return(model)

class model_buffer(deque):

  def __init__(self):
    super().__init__()
    self.ts = time()
    self.nr_images = 0
    self.img_rest = np.empty((0, xdim, ydim, 3), np.float32)
    self.pre_rest = None

  def append(self, item):
    # item[0] = model, item[1] = np.imagelist, item[2] = userindex
    super().append(item)
    self.nr_images += item[1].shape[0]
    self.ts = time()

  def get(self, maxcount):
    result = self.img_rest
    if self.img_rest.shape[0] > 0:
      self.len_user = [(self.img_rest.shape[0], self.img_rest_user, True)]
    else:
      self.len_user = []
    while (len(self) > 0) and (result.shape[0] < maxcount):
      item = self.popleft()
      self.nr_images -= item[1].shape[0]
      finished = ((result.shape[0] + item[1].shape[0]) <= maxcount)
      self.len_user.append((item[1].shape[0], item[2], finished))
      result = np.vstack((result, item[1]))
      self.img_rest = result[maxcount:]
      self.img_rest_user = item[2]
      result = result[:maxcount]
    return(result)

class tf_user(object):

  clientset = set()

  def __init__(self):
    i = 0
    while i in tf_user.clientset:
      i += 1
    tf_user.clientset.add(i)
    self.id = i
    self.fifoin = Queue(maxsize=8)
    self.fifoout = Queue()

  def __del__(self):
    tf_user.clientset.discard(self.id)

class c_tfworker:

  def __init__(self, max_nr_models=64):
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
      self.ws.connect(tfw_wsurl)
      outdict = {
        'code' : 'auth',
        'name' : tfw_wsname,
        'pass' : tfw_wspass,
      }
      self.ws.send(zlib.compress(json.dumps(outdict).encode()), opcode=2)
      MultiTimer(interval=20, function=self.send_ping, runonstart=False).start()
      #ws.close()

  def send_ping(self):
    if (time() - self.ws_ts) > 15:
      outdict = {'code' : 'ping',}
      self.ws.send(zlib.compress(json.dumps(outdict).encode()), opcode=2)

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
    if not (schoolnr in self.allmodels):
      self.allmodels[schoolnr] = {}
      self.allmodels[schoolnr]['time'] = myschool.lastfile
      if (gpu_sim >= 0) or tfw_wsurl:
        sleep(gpu_sim_loading) 
      else:
        tempmodel = load_model(myschool.dir+'model/cam-ai_model.h5', 
          custom_objects={'cmetrics': cmetrics, 'hit100': hit100,})
        self.allmodels[schoolnr]['weights'] = []
        self.allmodels[schoolnr]['weights'].append(
          tempmodel.get_layer(index=2).get_weights())
        self.allmodels[schoolnr]['weights'].append(
          tempmodel.get_layer(index=3).get_weights())
        self.allmodels[schoolnr]['weights'].append(
          tempmodel.get_layer(index=4).get_weights())
        del tempmodel
      logger.info('***** Got model file #'+str(schoolnr)+'...')
    if not (schoolnr in self.activemodels):
      if gpu_sim >= 0 or tfw_wsurl:
        sleep(gpu_sim_loading / 2)
        self.activemodels[schoolnr] = True
      else:
        if len(self.activemodels) < self.max_nr_models:
          self.activemodels[schoolnr] = makemodel()
          nr_to_replace = schoolnr
        else:
          nr_to_replace = min(self.activemodels, 
            key= lambda x: self.activemodels[x]['time']) 
          self.activemodels[schoolnr] = self.activemodels[nr_to_replace]
          del self.activemodels[nr_to_replace]
        self.activemodels[schoolnr].get_layer(index=2).set_weights(
          self.allmodels[schoolnr]['weights'][0])
        self.activemodels[schoolnr].get_layer(index=3).set_weights(
          self.allmodels[schoolnr]['weights'][1])
        self.activemodels[schoolnr].get_layer(index=4).set_weights(
          self.allmodels[schoolnr]['weights'][2])
      logger.info('***** Got model buffer #'+str(schoolnr)+'...')
    if test_pred:
      if (gpu_sim < 0) and (not tfw_wsurl):
        xdata = np.random.rand(8,331,331,3)
        self.activemodels[schoolnr].predict_on_batch(xdata)
      else:
        sleep(gpu_sim_loading / 3)
      logger.info('***** Testrun for model #'+str(schoolnr)+' done...')

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
      e_school = school.objects.get(id=schoolnr).e_school
      while True:
        ts_one = time()
        had_timeout = (self.model_buffers[schoolnr].ts + tfw_timeout) < time()
        if ((self.model_buffers[schoolnr].nr_images >= tfw_maxblock) 
            or (had_timeout and self.model_buffers[schoolnr].nr_images > 0)):
          self.model_buffers[schoolnr].ts = time()
          slice_to_process = self.model_buffers[schoolnr].get(tfw_maxblock)
          #logger.info('Out #'+str(schoolnr)+'#'+str(slice_to_process.shape[0]))
          self.check_model(schoolnr, logger)
          if gpu_sim >= 0:
            if gpu_sim > 0:
              sleep(gpu_sim)
            predictions = np.empty((0, len(classes_list)), np.float32)
            for i in slice_to_process:
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
          elif tfw_wsurl:
            self.ws_ts = time()
            outdict = {
              'code' : 'imgl',
              'scho' : e_school,
              'data' : slice_to_process.tolist(),
            }
            self.ws.send(zlib.compress(json.dumps(outdict).encode()), opcode=2)
            predictions = json.loads(self.ws.recv())
          else:
            slice_to_process = np.float32(slice_to_process)/255
            if slice_to_process.shape[0] < tfw_maxblock:
              patch = np.zeros((tfw_maxblock - slice_to_process.shape[0], 
                slice_to_process.shape[1], 
                slice_to_process.shape[2], 
                slice_to_process.shape[3]), 
                np.float32)
              portion = np.vstack((slice_to_process, patch))
              predictions = (
                self.activemodels[schoolnr].predict_on_batch(portion))
              predictions = predictions[:slice_to_process.shape[0]]
            else:
              predictions = (
                self.activemodels[schoolnr].predict_on_batch(slice_to_process))
          for item in self.model_buffers[schoolnr].len_user:
            subslice = predictions[:item[0]]
            predictions = predictions[item[0]:]
            if item[2]:
              if self.model_buffers[schoolnr].pre_rest is not None:
                subslice = np.vstack((self.model_buffers[schoolnr].pre_rest, 
                  subslice))
                self.model_buffers[schoolnr].pre_rest = None
              with self.users_lock:
                if item[1] in self.users:
                  self.users[item[1]].fifoout.put(subslice)
              #logger.info('In #'+str(schoolnr)+'>'+str(item[1])+'#'+str(subslice.shape[0]))
            else:
              self.model_buffers[schoolnr].pre_rest = subslice
              self.model_buffers[schoolnr].user_rest = item[1]
        else:
          sleep(0.01)
          break

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
            newitem = self.users[userindex].fifoin.get(block=False)
            break
          except Empty:
            newitem = None
            break
        if newitem is None:
          sleep(0.01)
        else:
          schoolnr = newitem[0]
          newitem.append(userindex)
          if schoolnr not in self.model_buffers:
            self.model_buffers[schoolnr] = model_buffer()
          self.model_buffers[schoolnr].append(newitem)

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


