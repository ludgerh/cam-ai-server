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

from json import dumps
from time import time
from threading import Lock
from .models import view, mask
from .c_tools import djconf
from .c_masks import mask_list
from .c_device import c_device
from .c_base import c_base

class c_view(c_device):

  def __init__(self, id=None):
    self.modelclass = view
    super().__init__(id, type='V')
    if self.id <= 0:
      self.v_index = 1000000
      while self.v_index in c_base.instances['V']:
        self.v_index += 1
      c_base.instances['V'][self.v_index] = self 
    self.sizecode = 'X'
    self.img_add = None
    self.drawpad = None
    self.showmask = True
    self.editmask = False
    self.whitemarks = False
    self.radius = 10
    self.mypoint = None
    self.parent = None
    self.mask_list = mask_list([])
    self.pm_lock = Lock()

  def setviewsize(self, sizecode):
    super().setviewsize(sizecode)
    if (self.parent.type == 'C') and (self.parent.int_mask_list is not None):
      self.mask_list = mask_list(
        self.parent.int_mask_list,
        self.xview / self.params['xres'], 
        self.yview / self.params['yres'], 
      )
    if self.mask_list is not None:
      self.refresh_mask()
      self.refresh_drawing()

  def refresh_drawing(self):
    self.drawpad = self.mask_list.make_drawpad(
      self.xview, 
      self.yview, (255,255,255), (0,0,0),
      self.radius,
    )

  def refresh_mask(self):
    self.img_add = self.mask_list.mask_from_polygons(
      self.xview, 
      self.yview, (255,255,255), (0,0,0)
    )

  def feed_back(self):
    self.parent.int_mask_list = self.mask_list.ints_from_mask(
      self.xview,
      self.params['xres'], 
      self.yview,
      self.params['yres'],
    )

  def make_new_ring(self):
    self.mask_list.new_ring(
      self.xview,
      self.yview,
    )

  def mousedownhandler(self, x, y):
    self.mypoint =  self.mask_list.point_clicked(x, y, self.radius) 

  def mousemovehandler(self, x, y):
    if self.mypoint is not None:
      self.mask_list.move_point(self.mypoint,
        min(max(x, 0),self.drawpad.shape[1] - 1),
        min(max(y, 0),self.drawpad.shape[0] - 1),
        self.drawpad, (0,0,0), self.radius)

  def mouseuphandler(self, x, y):
    self.mousemovehandler(x, y)
    if self.mypoint is not None:
      self.refresh_drawing()
      self.parent.int_mask_list = self.mask_list.ints_from_mask(
        self.xview,
        self.yview,
        self.params['xres'], 
        self.params['yres'],
      )
      self.parent.refresh_mask()
      self.refresh_mask()
      mask.objects.filter(cam_id=self.params['source_id']).delete()
      for ring in self.parent.int_mask_list:
        m = mask(
          name='New Ring',
          definition=dumps(ring),
          cam_id=self.params['source_id'],
        )
        m.save()
      self.mypoint = None

  def plus_1(self):
    self.parent.add_view_count()
    if self.parent.type == 'E':
      self.parent.set_cam_counts()

  def minus_1(self):
    if self.id == 0:
      self.parent.stop()
    else:
      self.parent.take_view_count()
    if self.parent.type == 'E':
      self.parent.set_cam_counts()






