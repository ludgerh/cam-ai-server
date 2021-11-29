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

from logging import getLogger, DEBUG, INFO, FileHandler as LogFileHandler, StreamHandler as LogStreamHandler, Formatter
from traceback import format_exc
from c_client.models import tag, event
from .l_tools import djconfig, logdict
from sys import argv
from os import path
djconf = djconfig()
pname = argv[0]
pname = path.split(pname)[1]
gpu_nr = 'X'
if (djconf.getconfigfloat('gpu_sim') < 0) and (not djconf.getconfig('tfw_wsurl','')):
  gpu_nr = '0'
if pname == 'c_trainer.py':
  gpu_nr = '1'
if gpu_nr != 'X':
  from os import environ
  environ['CUDA_DEVICE_ORDER']='PCI_BUS_ID'
  environ['CUDA_VISIBLE_DEVICES']=gpu_nr
  from tensorflow.keras import backend as K
	
taglist = tag.objects.filter(school=1)
classes_list = []
for item in taglist:
	if not item.name in classes_list:
		classes_list.append(item.name)

def rect_atob(rect):
	# Rectangle notation B: (x1, x2, y1, y2)
	return([rect[0], rect[0]+rect[2]-1, rect[1], rect[1]+rect[3]-1])

def rect_btoa(rect):
	# Rectangle notation A: (x1, y1, w, h)
	return([rect[0], rect[2], rect[1]-rect[0]+1, rect[3]-rect[2]+1])

def hasoverlap(rect1, rect2) : # Rectangles in notation B
	if ((rect1[1] >= rect2[0]) and (rect2[1] >= rect1[0]) 
    and (rect1[3] >= rect2[2]) and (rect2[3] >= rect1[2])):
		return(True)
	else :
		return(False)

def merge_rects(rect_list): # Rectangles in notation B
  while True:
    changed = False
    for i in range(len(rect_list)):
      if rect_list[i][0] > -1:
        for j in range(i+1, len(rect_list)):
          if ((rect_list[j][0] > -1) 
              and hasoverlap(rect_list[i], rect_list[j])):
            rect_list[i][0] = min(rect_list[i][0], rect_list[j][0])
            rect_list[i][1] = max(rect_list[i][1], rect_list[j][1])
            rect_list[i][2] = min(rect_list[i][2], rect_list[j][2])
            rect_list[i][3] = max(rect_list[i][3], rect_list[j][3])
            rect_list[j][0] = -1
            changed = True
    if not changed:
      break
  rect_list = [item for item in rect_list if item[0] > -1]
  return(rect_list)

def run_with_log(executor, task, logname):
  def newfunction():
    logger = getLogger(logname)
    logger.setLevel(DEBUG)
    fh = LogFileHandler(djconf.getconfig('logdir')+logname+'.log')
    fh.setLevel(logdict[djconf.getconfig('loglevel','INFO')])
    ch = LogStreamHandler()
    ch.setLevel(logdict[djconf.getconfig('loglevel','INFO')])
    formatter = Formatter("{asctime} [{levelname:8}] {message}",
      "%d.%m.%Y %H:%M:%S","{")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.info('Started Thread '+str(logname)+'...')
    try:
      task(logger)
    except:
      logger.error(format_exc())
      logger.handlers.clear()
    logger.info('Finished Thread '+str(logname)+'...')
    logger.handlers.clear()
    return()

  if executor:
    executor.submit(newfunction)
  else:
    newfunction()

def cmetrics(y_true, y_pred):
  y_true = K.round(y_true)
  y_pred = K.round(y_pred)
  ones = K.ones_like(y_true)
  return K.mean(K.abs(y_pred + y_true - ones), axis=-1)

def hit100(y_true, y_pred):
  y_true = K.round(y_true)
  y_pred = K.round(y_pred)
  maxline = K.max(K.abs(y_true - y_pred), axis=-1)
  ones = K.ones_like(maxline)
  return K.abs(maxline - ones)

