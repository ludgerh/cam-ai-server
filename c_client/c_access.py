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

from .models import access_control

class c_access():

  def __init__(self):
    self.read_list()

  def read_list(self):
    self.checklist = list(access_control.objects.all())

  def check(self, type, id, user, mode):
    if user.id is None:
      userid = -1
    else:
      userid = user.id
    mychecklist = self.checklist
    mychecklist = [item for item in mychecklist if (item.vtype==type 
      or ((type.upper() in {'C','D','E'}) and (item.vtype.upper()=='X')) or item.vtype=='0')]
    mychecklist = [item for item in mychecklist if (item.vid==id or item.vid==0)]
    mychecklist = [item for item in mychecklist if (item.u_g.upper()=='U' and (
      ((userid != 0) and (item.u_g_nr==userid or item.u_g_nr==0))
      or (item.u_g_nr == -1)))]
    mychecklist = [item for item in mychecklist if (item.r_w.upper()==mode.upper() or item.r_w=='0' or item.r_w.upper()=='W')]
    if len(mychecklist) > 0:
      return(True)
    else:
      return(False)

  def check_view(self, input, userid, mode):
    if self.check(input.source_type, input.source_id, userid, mode):
      return(True)
    else:
      return(False)

  def filter_views(self, input, userid, mode):
    output = []
    for item in input:
      if self.check_view(item, userid, mode):
        output.append(item)
    return(output)

  def check_school(self, input, userid, mode):
    if self.check('S', input.id, userid, mode):
      return(True)
    else:
      return(False)

  def filter_schools(self, input, userid, mode):
    output = []
    for item in input:
      if self.check_school(item, userid, mode):
        output.append(item)
    return(output)

  def check_cam(self, input, userid, mode):
    if self.check('C', input.id, userid, mode):
      return(True)
    else:
      return(False)

  def filter_cams(self, input, userid, mode):
    output = []
    for item in input:
      if self.check_cam(item, userid, mode):
        output.append(item)
    return(output)

access = c_access()
