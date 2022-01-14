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

from threading import Lock
from time import sleep
from .c_tools import djconf

# Frame Types:
# 1 : Jpeg Data
# 2 : Pillow Data
# 3 : opencv Data

# List structure:
#[0] : Type
#[1] :	Frame
#[2] : timestamp

class c_buffer:

  def __init__(self, getall=False):
    self.mylock = Lock()
    self.dictlock = Lock()
    self.onf_dict = {} #on new frame
    self.nextitem = None
    self.getall = getall


  def push_to_onf(self, onf):
    with self.dictlock:
	    index = 0
	    while index in self.onf_dict:
		    index += 1
	    self.onf_dict[index] = onf
    return(index)

  def pop_from_onf(self, index):
    with self.dictlock:
	    del self.onf_dict[index]

  def putframe(self, data):
    if self.getall:
      while self.nextitem is not None:
        sleep(djconf.getconfigfloat('short_brake', 0.01))
    self.nextitem = data
    with self.dictlock:
      for index in self.onf_dict:
        self.onf_dict[index]()

  def getframe(self):
    while self.nextitem is None:
        sleep(djconf.getconfigfloat('short_brake', 0.01))
    data = self.nextitem
    self.nextitem = None
    return(data)

  def getframeonly(self):
    while self.nextitem is None:
      sleep(djconf.getconfigfloat('short_brake', 0.01))
    data = self.nextitem[1]
    self.nextitem = None
    return(data)
