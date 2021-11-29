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

# Version 1.0
import os
import numpy as np
from datetime import datetime
from random import sample
from os import path, O_NONBLOCK
from fcntl import fcntl, F_GETFL, F_SETFL
from c_client.models import setting

logdict = {'NOTSET' : 0,
  'DEBUG' : 10,
  'INFO' : 20,
  'WARNING' : 30,
  'ERROR' : 40,
  'CRITICAL' : 50}

class lhconfig:

  def __init__(self, filename) :
    self.config = {}
    self.filename = filename
    if os.path.exists(filename) :
      infile = open(filename,"r")
      lines = infile.read().splitlines()
      infile.close
    else:
      lines = []
    for line in lines:
      if len(line) > 0:
	      stemp = line.split('-->')
	      self.config[stemp[0]] = stemp[1]
        
  def setconfig(self, param, value) : 
    self.config[param] = value
    outfile = open(self.filename,"w")
    for key in self.config :
      outfile.write(key+'-->'+self.config[key]+'\n')
    outfile.close
        
  def getconfig(self, param) :
    if param in self.config.keys(): 
      return(self.config[param])
    else :
      return(False)


class sqlconfig:

  def __init__(self, connection, db):
    self.config = {}
    self.db = db;
    self.connection = connection
    self.connection.execute("select setting, `index`, value from settings")
    lines = self.connection.fetchall()
    for line in lines:
      if line[0] not in self.config:
        self.config[line[0]] = {}
      self.config[line[0]][line[1]] = line[2]
        
  def setconfig(self, param, value, index=0):
    if param not in self.config:
      self.config[param] = {}
    self.config[param][index] = value
    query = "select comment from settings where setting = %s and `index` = 0 "
    params = (param) 
    self.connection.execute(query, params)
    line = self.connection.fetchone()
    if line:
      comment = line[0]
    else:
      comment = 'Nothing yet...'
    query = """replace into settings (setting, `index`, value, comment) 
      values (%s, %s, %s, %s) """
    if index > 0:
      comment = '...'
    params = (param, index, value, comment)
    self.connection.execute(query, params)

  def getconfig(self, param, default=None, index=0): 
    if not (isinstance(default, str) or (default is None)):
      default = str(default)
    if param in self.config: 
      if index in self.config[param]:
	      return(self.config[param][index])
      else:
	      if index == 0:
		      return(default)
	      else:
		      if 0 in self.config[param]:
			      return(self.config[param][0])
		      else:
			      return(default)
    else:
      return(default)

  def getconfigint(self, param, default=None, index=0):
    temp = self.getconfig(param, default, index)
    if temp:
      return(int(temp))
    else:
      return(default)

  def setconfigint(self, param, value, index=0) :
    self.setconfig(param, str(value), index)

  def getconfigfloat(self, param, default=None, index=0):
    temp = self.getconfig(param, default, index)
    if temp:
      return(float(temp))
    else:
      return(default)

  def setconfigfloat(self, param, value, index=0):
    self.setconfig(param, str(value), index)

  def getconfigbool(self, param, default=None, index=0):
    temp = self.getconfig(param, default, index)
    if temp:
      if temp in ('1', 'true', 'True', 'yes', 'Yes', 'ja', 'Ja'): 
	      return(True)
      elif temp in ('0', 'false', 'False', 'no', 'No', 'nein', 'Nein'): 
	      return(False)
      else:
	      return('NoBool: '+temp)
    else:
      return(default)

  def setconfigbool(self, param, value, index=0) :
    self.setconfig(param, str(value), index)



class djconfig(sqlconfig):

  def __init__(self):
    self.config = {}
    lines = setting.objects.all()
    for line in lines:
      if line.setting not in self.config:
	      self.config[line.setting] = {}
      self.config[line.setting][line.index] = line.value
        
  def setconfig(self, param, value, index=0):
    if param not in self.config:
      self.config[param] = {}
    self.config[param][index] = value
    try:
      line = setting.objects.get(setting=param, index=index)
      line.value = value
    except setting.DoesNotExist:
      line = setting(setting=param, index=index, value=value)
      if index > 0:
	      line.comment = '...'
      else:
	      line.comment = 'Nothing yet...'
    line.save()

  def getconfig(self, param, default=None, index=0): 
    if not (isinstance(default, str) or (default is None)):
      default = str(default)
    if param in self.config: 
      if index in self.config[param]:
	      return(self.config[param][index])
      else:
	      if index == 0:
		      return(default)
	      else:
		      if 0 in self.config[param]:
			      return(self.config[param][0])
		      else:
			      return(default)
    else:
      return(default)

def ts2mysql(rein) :
  return(datetime.fromtimestamp(rein).strftime('%Y-%m-%d %H:%M:%S'))

def ts2mysqltime(rein) :
  return(datetime.fromtimestamp(rein).strftime('%H:%M:%S'))

def ts2filename(rein, noblank=False) :
  if noblank:
    return(datetime.fromtimestamp(rein).strftime('%Y-%m-%d-%H-%M-%S-%f'))
  else:
    return(datetime.fromtimestamp(rein).strftime('%Y-%m-%d %H-%M-%S-%f'))

def uniquename(pathname, filename, extension):
#filename goes into result string, pathname does not
  stemp = filename
  counter = 0
  while path.exists(pathname+filename+'.'+extension):
    filename = stemp+'-'+str(counter)
    counter = counter+1
  return(filename+'.'+extension)

def randomfilter(outlength, *args):
  arglist = list(args)
  if len(arglist[0]) > outlength:
    randIndex = sample(range(len(args[0])), outlength)
    randIndex.sort()
    for i in range(len(arglist)):
      if type(arglist[i]) is list:
        arglist[i] = [arglist[i][j] for j in randIndex]
      elif isinstance(arglist[i], np.ndarray):
        print('+++', arglist[i].shape[0])
        print('!!!', len(randIndex))
        output = np.empty((0, arglist[i].shape[1]), arglist[i].dtype)
        for j in randIndex:
          if j < arglist[i].shape[0]:
            print(output.shape, arglist[i].shape)
            output = np.vstack((output, arglist[i][j]))
        arglist[i] = output
        print('---', arglist[i].shape[0])
  return(arglist)

def update_from_dict(instance, attrs, commit=True):
  for attr, val in attrs.items():
    setattr(instance, attr, val)
  if commit:
    instance.save()

def myreadlines(f, newline):
  buf = ""
  while True:
    while True:
      pos = None
      for i in range(len(newline)):
        try:
          found = buf.index(newline[i])
          if pos:
            pos = min(pos, found)
          else:
            pos = found
        except ValueError:
          pass
      if pos is None:		
        break
      else:
        yield buf[:pos]
        buf = buf[pos + len(newline):]
    chunk = f.read(4096)
    if not chunk:
      yield buf
      break
    buf += str(chunk)

class listplus(list):
  """
  A subclass of list that can accept additional attributes.
  Should be able to be used just like a regular list.

  The problem:
  a = [1, 2, 4, 8]
  a.x = "Hey!" # AttributeError: 'list' object has no attribute 'x'

  The solution:
  a = listplus(1, 2, 4, 8)
  a.x = "Hey!"
  print a       # [1, 2, 4, 8]
  print a.x     # "Hey!"
  print len(a)  # 4

  You can also do these:
  a = listplus( 1, 2, 4, 8 , x="Hey!" )                 # [1, 2, 4, 8]
  a = listplus( 1, 2, 4, 8 )( x="Hey!" )                # [1, 2, 4, 8]
  a = listplus( [1, 2, 4, 8] , x="Hey!" )               # [1, 2, 4, 8]
  a = listplus( {1, 2, 4, 8} , x="Hey!" )               # [1, 2, 4, 8]
  a = listplus( [2 ** b for b in range(4)] , x="Hey!" ) # [1, 2, 4, 8]
  a = listplus( (2 ** b for b in range(4)) , x="Hey!" ) # [1, 2, 4, 8]
  a = listplus( 2 ** b for b in range(4) )( x="Hey!" )  # [1, 2, 4, 8]
  a = listplus( 2 )                                     # [2]
  """
  def __new__(self, *args, **kwargs):
    return super(listplus, self).__new__(self, args, kwargs)

  def __init__(self, *args, **kwargs):
    if len(args) == 1 and hasattr(args[0], '__iter__'):
      list.__init__(self, args[0])
    else:
      list.__init__(self, args)
    self.__dict__.update(kwargs)

  def __call__(self, **kwargs):
    self.__dict__.update(kwargs)
    return self

def np_mov_avg(input, radius):
  if radius == 0:
    return(input)
  else:
    result = []
    for i in range(input.shape[0]):
      segment = np.average(input[max(0, i-radius):i+radius+1], 0)
      result.append(segment)
    result = np.stack(result)
    return(result)
