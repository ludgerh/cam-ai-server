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
import numpy as np
import cv2 as cv
from .models import detector
from .c_device import c_device
from .c_buffer import c_buffer
from .c_tools import rect_atob, rect_btoa, hasoverlap, merge_rects

class c_detector(c_device):

  def __init__(self, id=None):
	  self.modelclass = detector
	  self.firstdetect = True
	  self.ts_background = time()
	  super().__init__(id, type='D')

  def postinit(self):
    super().postinit()
    self.myeventer = self.instances['E'][self.params['eventer']]
    self.myeventer.mydetector = self

  def run(self, logger):
    self.logger = logger
    self.myeventer = self.instances['E'][self.params['eventer']]
    self.eventbuffer = self.myeventer.detectbuffer
    self.eventbuffer.xres = 0
    self.eventbuffer.yres = 0
    self.eventbuffer.name = self.params['name']
    super().run(logger)

  def run_one(self, input):
    frametime = input[2]
    frame = input[1]
    if self.firstdetect:
      self.background = np.float32(frame)
      self.buffer = frame
      self.firstdetect = False
    objectmaxsize = round(max(self.buffer.shape[0],self.buffer.shape[1])*self.params['max_size'])
    buffer1 = cv.absdiff(self.buffer, frame)
    buffer1 = cv.split(buffer1)
    buffer2 = cv.max(buffer1[0], buffer1[1])
    buffer1 = cv.max(buffer2, buffer1[2])
    ret, buffer1 = cv.threshold(buffer1,self.params['threshold'],255,cv.THRESH_BINARY)
    erosion = self.params['erosion']
    if (erosion > 0) :
      kernel = np.ones((erosion*2 + 1,erosion*2 + 1),np.uint8)
      buffer2 = cv.erode(buffer1,kernel,iterations =1)
    else:
      buffer2 = buffer1
    dilation = self.params['dilation']
    if (dilation > 0) :
      kernel = np.ones((dilation*2 + 1,dilation*2 + 1),np.uint8)
      buffer3 = cv.dilate(buffer2,kernel,iterations =1)
    else:
      buffer3 = buffer2
    mask = 255 - buffer3
    buffer1 = cv.cvtColor(buffer1, cv.COLOR_GRAY2BGR)
    buffer2 = cv.cvtColor(buffer2, cv.COLOR_GRAY2BGR) 
    buffer4 = cv.cvtColor(buffer3, cv.COLOR_GRAY2BGR)
    buffer1 = list(cv.split(buffer1))
    buffer1[1] = buffer1[1] * 0
    buffer1 = cv.merge(buffer1)
    buffer1 = cv.addWeighted(buffer4, 0.2, buffer1, 1, 0)
    buffer1 = cv.addWeighted(buffer1, 1, buffer2, 1, 0)
    rect_list = []
    if dilation == 0:
      grid = 2
    else:
      grid = dilation*2
    xmax = buffer3.shape[1]-1
    for x in range(0,xmax+grid,grid):
      if x < xmax + grid:
        x = min(x, xmax)
        ymax = buffer3.shape[0]-1
        for y in range(0,ymax+grid,grid):
          if y < ymax + grid:
            y = min(y, ymax)
            if (buffer3[y,x] == 255) :
	            retval, image, dummy, recta = cv.floodFill(buffer3, None,
		            (x, y), 100)
	            rectb = rect_atob(recta)
	            rectb.append(False)
	            rect_list.append(rectb)
	            recta = rect_btoa(rectb)
    rect_list = merge_rects(rect_list)
    sendtime = frametime
    for rect in rect_list[:self.params['max_rect']]:
      recta = rect_btoa(rect)
      cv.rectangle(buffer1, recta, (200), 5)
      if ((recta[2]<=objectmaxsize) and (recta[3]<=objectmaxsize)):
        if ((self.myeventer.view_count > 0) 
            or (self.myeventer.record_count > 0) 
            or (self.myeventer.data_count > 0)):
          aoi = np.copy(frame[rect[2]:rect[3], rect[0]:rect[1]])
          self.eventbuffer.putframe((3, aoi, sendtime, rect[0], rect[1], rect[2], rect[3]))
        sendtime += 0.000001
      else:
        self.background = np.float32(frame)
    if self.params['backgr_delay'] == 0:
      self.buffer = frame
    else:
      if (time() >= (self.ts_background + self.params['backgr_delay'])): 
        self.ts_background = time()
        cv.accumulateWeighted(frame, self.background, 0.1)
      else:
        cv.accumulateWeighted(frame, self.background, 0.5, mask)
      self.buffer = np.uint8(self.background)
    return((3, buffer1, frametime))

