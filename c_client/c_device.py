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

import json
from django.utils import timezone
from time import sleep, time
from .c_tools import djconf
from .c_base import c_base
from .c_buffer import c_buffer

class speedlimit:
  def __init__(self):
    self.ts1 = 0
    self.ts2 = 0

  def greenlight(self, time):
    return((self.ts2 - self.ts1) >= time)

class speedometer:
  def __init__(self):
    self.ts1 = 0
    self.ts2 = time()
    self.counter = 0
    self.timeadd = 0.0

  def gettime(self):
    if self.ts1 == 0:
      result = 0.0
    else:
      self.counter += 1
      self.timeadd += (self.ts2 - self.ts1)
      if self.timeadd >= 10:
        result = (self.counter / self.timeadd)
        self.counter = 0
        self.timeadd = 0.0
      else:
        result = None
    self.ts1 = self.ts2
    self.ts2 = time()
    return(result)

class c_device(c_base):

  def __init__(self, id=None, type='X'):
    super().__init__(id)
    self.type = type
    self.view_count = 0
    self.record_count = 0
    self.data_count = 0
    self.running = False
    if self.type in {'V', 'D', 'E'}:
      self.inbuffer = c_buffer(getall=False)
    else:
      self.inbuffer = None
    if self.id > 0:
      c_base.instances[self.type][self.id] = self 
    # see else-clause in c_view.py
    self.finished = True
    if not id:
      self.setparams({'made' : timezone.now(),}, writedb=True)
    if self.id == 0:
      self.outbuffers = []
    else:
      self.outbuffers = json.loads(self.params['outbuffers'])

  def add_view_count(self):
    self.view_count += 1
    #print('V+++', self.type, self.id, self.view_count)
    if self.type != 'C':
      self.parent.add_data_count()

  def take_view_count(self):
    self.view_count = max(0, self.view_count - 1)
    #print('V---', self.type, self.id, self.view_count)
    if self.type != 'C':
      self.parent.take_data_count()

  def add_record_count(self):
    self.record_count += 1
    #print('R+++', self.type, self.id, self.record_count)
    if self.type != 'C':
      self.parent.add_record_count()

  def take_record_count(self):
    self.record_count = max(0, self.record_count - 1)
    #print('R---', self.type, self.id, self.record_count)
    if self.type != 'C':
      self.parent.take_record_count()

  def add_data_count(self):
    self.data_count += 1
    #print('D+++', self.type, self.id, self.data_count)
    if self.type != 'C':
      self.parent.add_data_count()

  def take_data_count(self):
    self.data_count = max(0, self.data_count - 1)
    #print('D---', self.type, self.id, self.data_count)
    if self.type != 'C':
      self.parent.take_data_count()

  def setviewsize(self, sizecode):
	  self.sizecode = sizecode
	  if self.sizecode == 'S':
		  paramtxt = 'i_width_small'
		  mydefault = 540
	  elif self.sizecode == 'L':
		  paramtxt = 'i_width_large'
		  mydefault = 1600
	  self.xview = djconf.getconfigint(paramtxt, mydefault)
	  self.yview = round(self.params['yres'] / self.params['xres'] * self.xview)
	  if self.yview > self.xview:
		  xbuffer = self.xview
		  self.xview  = round(self.xview / self.yview * self.xview)
		  self.yview = xbuffer

  def postinit(self):
    self.view_object = None
    self.children = []
    for item in self.outbuffers:
      nextmodule = c_base.instances[item[0]][item[1]]
      self.children.append(nextmodule)
      nextmodule.parent = self
      if item[0] == 'V':
        nextmodule.setparams({
          'source_type' : self.type,
          'source_id' : self.id,
        }, writedb=True)
        if not self.view_object:
          self.view_object = nextmodule
      nextmodule.setparams({
        'name' : self.params['name'],
        'xres' : self.params['xres'],
        'yres' : self.params['yres'],
      }, writedb=True)

  def stop(self):
    self.running = False
    self.setparams({'lastused' : timezone.now(),}, writedb=True)

  def put_one(self, frameitem):
    if self.id == 0:
      for item in self.children:
        item.inbuffer.putframe(frameitem)
    else:
      for item in self.outbuffers:
        outbuffer = c_base.instances[item[0]][item[1]].inbuffer
        outbuffer.putframe(frameitem)
    fps = self.som.gettime()
    if not (self.type == 'C'):
      if fps is not None:
        self.setparams({'fpsactual' : fps,}, writedb=True)

  def run(self, logger=None):
    self.finished = False
    self.running = True
    if self.params['fpslimit'] == 0:
      self.period = 0.0
    else:
      self.period = 1.0 / self.params['fpslimit']
    sl = speedlimit()
    self.som = speedometer()
    while self.running:
      while True:
        if ((self.view_count == 0) and (self.record_count == 0) 
            and (self.data_count == 0) and (self.type != 'C')):
          sleep(0.01)
        else:
          break
      if self.inbuffer:
        input = self.inbuffer.getframe()
        sl.ts2 = input[2]
      else:
        input = None
        sl.ts2 = time()
      if (self.type == 'C') or sl.greenlight(self.period):
        result = self.run_one(input)
        if result is None:
          sleep(0.01)
        else:
          self.put_one(result)
          sl.ts1 = sl.ts2
      else:
        sleep(0.01)
    self.finished = True
