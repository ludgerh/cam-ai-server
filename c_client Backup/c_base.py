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

from time import sleep
from django.forms.models import model_to_dict
from django.db import transaction, connection
from django.db.utils import OperationalError

class c_base:

  instances = {}
  instances['V'] = {}
  instances['C'] = {}
  instances['D'] = {}
  instances['E'] = {}

  def __init__(self, id=None):
    self.type = '?'
    self.id = id
    if self.id is None:
      with transaction.atomic():
        dbline = self.modelclass(**{}) 
        dbline.save()
        self.id =  self.modelclass.objects.latest('id').id
    if self.id == 0:
      self.params = {}
    else:
      self.getparams()

  def getparams(self):
    dbline = self.modelclass.objects.get(id=self.id)
    self.params = model_to_dict(dbline)

  def setparams(self, pdict, writedb=False):
    for attr, val in pdict.items():
      self.params[attr] = val
    if writedb and (self.id > 0):
      while True:
        try:
          with transaction.atomic():
            dbline = self.modelclass.objects.get(id=self.id)	
            for attr, val in pdict.items():
              setattr(dbline, attr, val)
            dbline.save()
          break
        except OperationalError:
          connection.close()

