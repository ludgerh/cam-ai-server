#!/usr/bin/env python
# coding: utf-8

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

from os import path, remove, rename, environ
environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
environ["CUDA_VISIBLE_DEVICES"]="1"
from statistics import mean
from time import time
from random import seed, uniform, shuffle, sample, choice
from sys import platform
from math import ceil, pi, sqrt
import numpy as np
from shutil import copyfile

from .l_tools import ts2filename
from .c_tools import djconf, classes_list, cmetrics, hit100
from .hwcheck import getcputemp, getcpufan1, getcpufan2, getgputemp, getgpufan
from .models import trainframe, fit as sqlfit, epoch, school
from .c_schools import catfilterdict, get_newline_count, reset_newline_count
from django.utils import timezone
from django.db import connection as sqlconnection
import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, Callback
from tensorflow.keras.utils import Sequence
from tensorflow.keras import backend as K


class sql_sequence(Sequence):
  def __init__(self, sqlresult, xdim, ydim, 
      normalisation=None,
      batch_size=32, 
      class_weights=None, 
      model=None,
      save_to_dir=None,
      save_prefix="",
      rotation_range=0,
      width_shift_range=0,
      height_shift_range=0,
      brightness_range=0,
      shear_range=0,
      zoom_range=None,
      horizontal_flip=False,
      vertical_flip=False,):
    self.sqlresult = sqlresult
    self.batch_size = batch_size
    self.xdim = xdim
    self.ydim = ydim
    self.normalisation = normalisation
    self.class_weights = class_weights
    self.model = model
    self.save_to_dir=save_to_dir
    self.save_prefix=save_prefix
    self.rotation_range=rotation_range
    self.width_shift_range=width_shift_range
    self.height_shift_range=height_shift_range
    self.brightness_range=brightness_range
    self.shear_range=shear_range
    self.zoom_range=zoom_range
    self.horizontal_flip=horizontal_flip
    self.vertical_flip=vertical_flip

  def __len__(self):
    return ceil(len(self.sqlresult) / self.batch_size)

  def __getitem__(self, idx):
    batch_slice = self.sqlresult[idx*self.batch_size:(idx + 1)*self.batch_size]
    xdata = []
    ydata = np.empty(shape=(len(batch_slice), len(classes_list)))

    if (self.rotation_range or self.width_shift_range or self.height_shift_range 
      or self.shear_range or self.zoom_range):
      averages = []
    else:
      averages = None
    for i in range(len(batch_slice)):
      bmpdata = tf.io.read_file(batch_slice[i][1])
      bmpdata = tf.io.decode_bmp(bmpdata, channels=3)
      bmpdata = tf.image.resize(bmpdata, [self.xdim,self.ydim])
      if self.normalisation:
        bmpdata = tf.math.truediv(bmpdata, self.normalisation)
      if self.brightness_range > 0:
        bmpdata = tf.image.random_brightness(bmpdata, self.brightness_range)
      if self.normalisation:
        bmpdata = tf.clip_by_value(bmpdata, 0.00001, 255 / self.normalisation)
      else:
        bmpdata = tf.clip_by_value(bmpdata, 0.00001, 255)
      if averages is not None:
        average = tf.math.reduce_mean(bmpdata, (0, 1))
        average = [average] * self.ydim
        average = tf.stack(average)
        average = [average] * self.xdim
        average = tf.stack(average)
        averages.append(average)
      xdata.append(bmpdata)
      for j in range(len(classes_list)):
        ydata[i][j] = round(batch_slice[i][j+2])
    xdata = tf.stack(xdata)
    ydata = tf.convert_to_tensor(ydata)
    if averages is not None:
      averagedata = tf.stack(averages)
    else:
      averagedata = None

    if self.class_weights is not None:
      wdata = np.zeros(shape=(len(batch_slice)))

      predictions = self.model.predict_on_batch(xdata)
      for i in range(len(batch_slice)):
        wdata[i] = 1.0
        for j in range(len(self.class_weights)-1):
          if ydata[i,j] > 0.5:
            wdata[i] += self.class_weights[j]
        if wdata[i] <= 0.0:
          wdata[i] = self.class_weights[len(self.class_weights) - 1]

        for j in range(len(classes_list)):
          if round(predictions[i][j]) != ydata[i][j]:
            wdata[i] += 1.0;

    if self.horizontal_flip:
      xdata = tf.image.random_flip_left_right(xdata)
    if self.vertical_flip:
      xdata = tf.image.random_flip_up_down(xdata)
    if self.rotation_range > 0:
      angles = [uniform(self.rotation_range*-1,self.rotation_range) * pi / 180 
        for x in range(len(batch_slice))]
      xdata = tfa.image.rotate(xdata, angles)
    if (self.width_shift_range > 0) or (self.height_shift_range > 0):
      matrixes = []
      for x in range(len(batch_slice)):
        xshift = uniform(self.width_shift_range*-1,
	        self.width_shift_range)*self.xdim
        yshift = uniform(self.height_shift_range*-1,
	        self.height_shift_range)*self.ydim
        matrix = [1,0,xshift,0,1,yshift,0,0]
        matrixes.append(matrix)
      matrixes = tf.convert_to_tensor(matrixes)
      xdata = tfa.image.transform(xdata, matrixes)
    if self.shear_range > 0:
      matrixes = []
      for x in range(len(batch_slice)):
        shear_lambda = self.shear_range / 45
        shear_lambda = uniform(shear_lambda*-1,shear_lambda)
        matrix = [1.0,shear_lambda,0,0,1.0,0,0,0]
        matrixes.append(matrix)
      matrixes = tf.convert_to_tensor(matrixes)
      xdata = tfa.image.transform(xdata, matrixes)
    if self.zoom_range is not None:
      matrixes = []
      for x in range(len(batch_slice)):
        xyfactor = 1/uniform(self.zoom_range[0],self.zoom_range[1])
        xshift = round(self.xdim * (1 / xyfactor - 1) * 0.5 * xyfactor)
        yshift = round(self.ydim * (1 / xyfactor - 1) * 0.5 * xyfactor)
        matrix = [xyfactor,0,xshift,0,xyfactor,yshift,0,0]
        matrixes.append(matrix)
      matrixes = tf.convert_to_tensor(matrixes)
      xdata = tfa.image.transform(xdata, matrixes)
    if averagedata is not None:
      xdata = tf.where(tf.equal(xdata, 0), averagedata, xdata)
    del averagedata

    if self.save_to_dir is not None:
      for i in range(len(batch_slice)):
        if self.normalisation:
          stored = tf.math.multiply(xdata[i], self.normalisation)
        else:
          stored = xdata[i]
        stored = tf.dtypes.cast(stored,tf.uint8)
        stored = tf.io.encode_jpeg(stored)
        print(self.save_to_dir+self.save_prefix+ts2filename(time())+'.jpg')
        tf.io.write_file(self.save_to_dir+self.save_prefix
	        +ts2filename(time())+'.jpg', stored)
        del stored

    if self.class_weights is None:
      return(xdata, ydata)
    else:
      return(xdata, ydata, wdata)

  def on_epoch_end(self):
    if self.class_weights is not None:
      shuffle(self.sqlresult)

class MyCallback(Callback):
  def __init__(self, myfit):
    super().__init__()
    self.myfit = myfit

  def on_epoch_end(self, myepoch, logs=None):
    myepoch = epoch(fit=self.myfit, 
      loss = float(logs['loss']),
      cmetrics = float(logs['cmetrics']),
      hit100 = float(logs['hit100']),
      val_loss = float(logs['val_loss']),
      val_cmetrics = float(logs['val_cmetrics']),
      val_hit100 = float(logs['val_hit100']),
    )
    myepoch.save()
    sqlconnection.close()

def getlines(myschool, allschools, filter= False, getallschools=False):
  schooldict = {}
  for i in allschools:
    schooldict[i.id] = i.dir
  filterdict = {}
  filterdict['school'] = myschool.id
  filterdict['checked'] = 1
  filterdict['code'] = 'TR'
  trcount = trainframe.objects.filter(**filterdict).count()
  filterdict['code'] = 'VA'
  vacount = trainframe.objects.filter(**filterdict).count()
  filterdict['code'] = 'NE'
  idlines = trainframe.objects.filter(**filterdict).values_list('id', flat=True)
  print('My Model: TR', trcount, 'VA', vacount, 'NE', len(idlines))
  for idline in idlines:
    if (((trcount + vacount) == 0) or
      ((vacount / (trcount + vacount)) 
        >= djconf.getconfigfloat('validation_split', 0.33333333))):
      newcode = 'TR'
      trcount += 1
    else:
      newcode = 'VA'
      vacount += 1
    line = trainframe.objects.get(id=idline)
    line.code = newcode
    line.save()
  result = {}
  if getallschools:
    del filterdict['school']
  for code in ['TR', 'VA']:
    filterdict['code'] = code
    sqlresult = trainframe.objects.filter(**filterdict)
    if filter:
      sqlresult = sqlresult.exclude(**catfilterdict)
    templist = []
    for i in range(len(sqlresult)):
      if sqlresult[i].school in schooldict:
        templine = [sqlresult[i].id, schooldict[sqlresult[i].school] + sqlresult[i].name,
          sqlresult[i].c0, sqlresult[i].c1, sqlresult[i].c2, sqlresult[i].c3,
          sqlresult[i].c4, sqlresult[i].c5, sqlresult[i].c6, sqlresult[i].c7,
          sqlresult[i].c8, sqlresult[i].c9, sqlresult[i].code,
        ]
        templist.append(templine)
    result[code] = templist
  print('Merged Model: TR', len(result['TR']), 'VA', len(result['VA']))
  return(result)

def train_once(myschool):
  seed()
  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  model_name = myschool.model_type
  #model_name = 'efficientnetv2s'
  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  allschools = school.objects.filter(active=1, used_by_others=True)
  if myschool.used_by_others==False:
    allschools = allschools | school.objects.filter(id=myschool.id)
  epochs = djconf.getconfigint('tr_epochs', 1000)
  batchsize = djconf.getconfigint('tr_batchsize', 32)
  val_split = djconf.getconfigfloat('validation_split', 0.33333333)
  mypatience = djconf.getconfigint('patience', 6)

  print('*******************************************************************');
  print('*** Working on School #'+str(myschool.id)+', '+myschool.name+'...');
  print('*******************************************************************');

  print("TensorFlow version: ", tf.__version__)
  device_name = tf.test.gpu_device_name()
  if device_name:
	  print('Found GPU at: {}'.format(device_name))
  else:
	  print('GPU device not found')

  if myschool.train_on_all:
    newlines = 0
    for item in allschools:
	    newlines += get_newline_count(item, myschool.do_filter)
  else:
	  newlines = get_newline_count(myschool, myschool.do_filter)
  print(newlines, 'new lines available, ', myschool.trigger, 'required.')
  if newlines >= myschool.trigger:
    print('Used model size:',myschool.size)
    templist = getlines(myschool, allschools, myschool.do_filter, myschool.train_on_all)
    trlist = templist['TR']
    valist = templist['VA']
    if (len(trlist) + len(valist)) < 50:
      print('*** Not enough frames...')
      print(len(trlist) + len(valist), 'is not enough, minimum is 50...')
      print('')
      return(False)

    if ((myschool.size > 0) 
	      and ((myschool.size) < (len(trlist) + len(valist)))):
      templist = trlist + valist
      for line in templist:
	      activeones = []
	      for i in range(9):
		      if line[i + 3] > 0.5:
			      activeones.append(i + 1)
	      if len(activeones) == 0:
		      line.append(0)
	      elif len(activeones) == 1:
		      line.append(activeones[0])
	      else:
		      line.append(choice(activeones))

      counters = [0] * len(classes_list)
      for line in templist:
	      for i in range(len(classes_list)):
		      if line[14] == i:
			      counters[i] += 1
      counters = [(counters[i],i) for i in range(len(classes_list))]
      counters.sort()
      print('*****',counters)
      placesleft = myschool.size
      classesleft = len(classes_list)
      newlist = []
      for item in counters:
	      lastplaces = placesleft
	      addition = [x for x in templist if  x[14] == item[1]]
	      if item[0] <= (placesleft // classesleft):
		      placesleft -= item[0]
	      else:
		      addition = sample(addition, placesleft // classesleft)
		      placesleft -= placesleft // classesleft
	      classesleft -= 1
	      newlist += addition
	      print('***',placesleft,lastplaces-placesleft,classesleft)
      trlist = [i for i in newlist if i[12] == 'TR'] 
      valist = [i for i in newlist if i[12] == 'VA'] 
  else:
	  print('*** Waiting for more frames...')
	  print(myschool.trigger - newlines, 'missing')
	  print('')
	  return(False)

  ts_start = timezone.now()

  weightarray = [0] * (len(classes_list) + 1)

  if sqlfit.objects.filter(school=myschool.id).exists():
	  fitnr = sqlfit.objects.filter(school=myschool.id).latest('id').id
  else:
	  fitnr = -1
  copyfile(myschool.dir+'model/'+model_name+'.h5', myschool.dir+'model/'+model_name+'_'+str(fitnr)+'.h5')
  if path.exists(myschool.dir+'model/'+model_name+'.h5'):
    model_to_load = myschool.load_model_nr
  else:
    model_to_load = 1
  for item in allschools:
    if item.id == model_to_load:
      path_for_load = item.dir
      break
    else:
      if item.id == 1:
        path_for_load = item.dir
  print('*** Loading model '+path_for_load+'...');
  model = load_model(path_for_load+'model/'+model_name+'.h5', 
	  custom_objects={'cmetrics': cmetrics,
		  'hit100': hit100,})
  xdim = model.layers[0].input_shape[1]
  ydim = model.layers[0].input_shape[2]
  description = "xdim: " + str(xdim) + "  ydim: " + str(ydim)
  description += "  epochs: " + str(epochs) + "  batchsize: " + str(batchsize)
  description += "  val_split: " + str(val_split) + "  min. l_rate: " 
  description += myschool.l_rate_min + "  max. l_rate: "
  description += myschool.l_rate_max + "\n" 
  description += ("  patience: " + str(mypatience)) + "\n" 
  l_rate = model.optimizer.learning_rate.numpy()
  print('>>> Learning rate from the model:', l_rate)
  l_rate = max(l_rate, float(myschool.l_rate_min))
  if float(myschool.l_rate_max) > 0:
    l_rate = min(l_rate, float(myschool.l_rate_max))
  print('>>> New learning rate:', l_rate)
  K.set_value(model.optimizer.learning_rate, l_rate)
  model.compile(loss='binary_crossentropy',
	  optimizer=Adam(learning_rate=l_rate),
	  metrics=[hit100, cmetrics])
  stringlist = []
  model.summary(print_fn=lambda x: stringlist.append(x))
  short_model_summary = "\n".join(stringlist)
  description += short_model_summary

  print(description)

  for i in range(len(trlist)):
	  found_class = False
	  for count in range(len(classes_list)):
		  if trlist[i][count+2] >= 0.5:
			  weightarray[count] += 1
			  found_class = True
	  if (not found_class):
		  weightarray[len(classes_list)] += 1

  print(classes_list)
  print(weightarray)
  normweight = 0
  normcount = 0
  class_weights = {}
  for i in range(len(weightarray)) : 
	  if weightarray[i] == 0:
		  class_weights[i] = 0
	  else:
		  class_weights[i] = (1.0 / weightarray[i])
	  normweight += (weightarray[i] * class_weights[i])
	  normcount += weightarray[i]
  for i in range(len(weightarray)) : 
    class_weights[i] = (class_weights[i] * normcount) / (normweight * 100)
    class_weights[i] = min(class_weights[i], 1.0)
  print(class_weights)

  if model_name == 'nasnetlarge':
    normalisation = 255.0
  else:
    normalisation = None
  train_sequence = sql_sequence(trlist, xdim, ydim,
    normalisation = normalisation,
    batch_size=batchsize, 
    class_weights=class_weights, 
    model=model,
    #save_to_dir='/home/ludger/temp/',
    #save_prefix='test'
    rotation_range=5,
    width_shift_range=0.2,
    height_shift_range=0.2,
    brightness_range=0.5,
    shear_range=0.2,
    zoom_range=(0.75, 1.25),
    horizontal_flip=True,
    vertical_flip=False,
  )

  description += """
*** Image Augmentation ***
	train_sequence = sql_sequence(trlist, xdim, ydim, normalisation,
		batch_size=batchsize, 
		class_weights=class_weights, 
		model=model,
		#save_to_dir='/home/ludger/temp/',
		#save_prefix='test',
		rotation_range=5,
    width_shift_range=0.2,
    height_shift_range=0.2,
		brightness_range=0.5,
    shear_range=0.2,
		zoom_range=(0.75, 1.25),
    horizontal_flip=True,
    vertical_flip=False,)
"""

  vali_sequence = sql_sequence(valist, xdim, ydim,
	  batch_size=batchsize)

  myfit = sqlfit(made=ts_start, 
	  minutes = 0.0, 
	  school = myschool.id, 
	  epochs = 0, 
	  nr_tr =len(trlist),
	  nr_va = len(valist),
	  loss = 0.0, 
	  cmetrics = 0.0, 
	  hit100 = 0.0, 
	  val_loss = 0.0, 
	  val_cmetrics = 0.0, 
	  val_hit100 = 0.0, 
	  cputemp = 0.0, 
	  cpufan1 = 0.0, 
	  cpufan2 = 0.0, 
	  gputemp = 0.0, 
	  gpufan = 0.0, 
	  description = description,
  )
  myfit.save()

  es = EarlyStopping(monitor='val_loss', mode='min', verbose=1,
    min_delta=0.0001, patience=mypatience)
  mc = ModelCheckpoint(myschool.dir+'model/'+model_name+'_temp.h5', 
	  monitor='val_loss', mode='min', verbose=1, save_best_only=True)
  reduce_lr = ReduceLROnPlateau(monitor='val_loss', mode='min', factor=sqrt(0.1),
	  patience=3, min_lr=0.0000001, min_delta=0.0001, verbose=1)
  cb = MyCallback(myfit)

  sqlconnection.close()

  history = model.fit(
	  x=train_sequence,
	  validation_data=vali_sequence,
    shuffle=False,
	  epochs=epochs, 
	  verbose=2,
	  callbacks=[es, mc, reduce_lr, cb,],
	  #use_multiprocessing=True,
	  )

  cputemp = getcputemp()
  cpufan1 = getcpufan1()
  cpufan2 = getcpufan2()
  if cpufan2 is None:
	  cpufan2 = 0
  gputemp = getgputemp(1)
  if gputemp is None:
	  gputemp = 0
  gpufan = getgpufan(1)
  if gpufan is None:
	  gpufan = 0

  if (platform.startswith('win') 
		  and path.exists(myschool.dir+'model/'+model_name+'.h5')):
	  remove(myschool.dir+'model/'+model_name+'.h5')
  rename(myschool.dir+'model/'+model_name+'_temp.h5', 
	  myschool.dir+'model/'+model_name+'.h5')
  model = load_model(myschool.dir+'model/'+model_name+'.h5', 
	  custom_objects={'cmetrics': cmetrics,
		  'hit100': hit100,})

  line = school.objects.get(id=myschool.id)
  line.lastfile = timezone.now()
  line.save()

  if myschool.train_on_all:
    for item in allschools:
	    reset_newline_count(item, myschool.do_filter)
  else:
	  reset_newline_count(myschool, myschool.do_filter)

  if len(history.history['loss'])	>= epochs:
	  mypatience = 0
  epochs = len(history.history['loss'])	
  if epochs < mypatience + 1:
	  mypatience = epochs - 1 
  myfit.minutes = (timezone.now()-ts_start).total_seconds() / 60
  myfit.epochs = epochs
  myfit.loss = float(history.history['loss'][epochs-mypatience-1])
  myfit.cmetrics = float(history.history['cmetrics'][epochs-mypatience-1])
  myfit.hit100 = float(history.history['hit100'][epochs-mypatience-1])
  myfit.val_loss = float(history.history['val_loss'][epochs-mypatience-1])
  myfit.val_cmetrics = float(history.history['val_cmetrics'][epochs-mypatience-1])
  myfit.val_hit100 = float(history.history['val_hit100'][epochs-mypatience-1])
  myfit.cputemp = cputemp
  myfit.cpufan1 = cpufan1
  myfit.cpufan2 = cpufan2
  myfit.gputemp = gputemp
  myfit.gpufan = gpufan
  myfit.save()

  print('***  Done  ***')
  print('')

  return(True)
