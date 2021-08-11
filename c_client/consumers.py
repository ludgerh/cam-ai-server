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
from PIL import Image
import cv2 as cv
from time import sleep, time
from random import randint
import numpy as np
import os
import zlib
from shutil import move
from hashlib import pbkdf2_hmac
from django.db.models import Q
from django.db import transaction
from django.core import serializers
from django.conf import settings
from django.forms.models import model_to_dict
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from autobahn.exception import Disconnected
from c_client.models import trainframe, tag, userinfo, event, event_frame, school, evt_condition, repeater, view_log
from .c_tools import djconf, classes_list
from .c_base import c_base
from .c_view import c_view
from .c_tfworker import tfworker
from .c_schools import get_taglist
from .c_access import access

#*****************************************************************************
# TrainDBUtilConsumer
#*****************************************************************************

class TrainDBUtilConsumer(AsyncWebsocketConsumer):

  def __init__(self):
    super().__init__()

  @database_sync_to_async
  def gettags(self, myschool):
    return([line.description for line in get_taglist(myschool)])

  @database_sync_to_async
  def gettrainimages(self, filterdict):
    lines = []
    for line in trainframe.objects.filter(
        **filterdict).filter(Q(code='TR') | Q(code='VA') | Q(code='NE')):
      if line.made_by is None:
        made_by = ''
      else:
        made_by = line.made_by.username
      lines.append({'id' : line.id, 
      'name' : line.name, 
      'made_by' : made_by,
      'cs' : [line.c0,line.c1,line.c2,line.c3,line.c4,line.c5,line.c6,
        line.c7,line.c8,line.c9,],})
    return(lines)

  @database_sync_to_async
  def getimagelist(self, idxs, is_school):
    imglist = np.empty((0,self.xdim, self.ydim, 3), np.uint8)
    for item in idxs:
      try:
        if is_school:
	        frame = event_frame.objects.get(id=item)
	        imagepath = djconf.getconfig('schoolframespath')+frame.name
        else:
	        frame = trainframe.objects.get(id=item)
	        mymodel = school.objects.get(id=frame.school)
	        imagepath = mymodel.dir+frame.name
        np_image = Image.open(imagepath)
        np_image = cv.resize(np.array(np_image),
          (djconf.getconfigint('tr_xdim', 331), djconf.getconfigint('tr_ydim', 331)))
        np_image = np.expand_dims(np_image, axis=0)
        imglist = np.append(imglist, np_image, 0)
      except FileNotFoundError:
        print('File not found:', imagepath)
    return(imglist)

  @database_sync_to_async
  def deltrainframe(self, idx):
    mytrainframe = trainframe.objects.get(id=idx)
    if access.check('S', mytrainframe.school, self.user, 'W'):
      mytrainframe.delete()
    return('OK')

  @database_sync_to_async
  def checkall(self, filterdict):
    if access.check('S', filterdict['school'], self.user, 'W'):
      trainframe.objects.filter(**filterdict).update(checked = 1)
    return('OK')

  @database_sync_to_async
  def deleteall(self, filterdict):
    if self.scope['user'].is_superuser:
      trainframe.objects.filter(**filterdict).delete()
    return('OK')

  async def connect(self):
    self.user = self.scope['user']
    self.tf_w_index = None
    self.maxblock = djconf.getconfigint('tfw_maxblock', 8)
    await self.accept()

  async def disconnect(self, close_code):
    if self.tf_w_index is not None:
      tfworker.unregister(self.tf_w_index) 

  async def receive(self, text_data):
    if settings.DEBUG:
      print('<--', text_data)
    params = json.loads(text_data)['data']
    if ((params['command'] == 'gettags') 
        or self.scope['user'].is_authenticated):
      outlist = {'tracker' : json.loads(text_data)['tracker']}
    else:
      await self.close()

    if params['command'] == 'gettrainimages' :
      filterdict = {'school' : params['model']}

      if params['cbnot']:
        if not params['cbchecked']:
	        filterdict['checked'] = 0
      else:
        if params['cbchecked']:
	        filterdict['checked'] = 1
        else:
	        filterdict['checked'] = -1 #Never
      if params['class'] == -2:
        pass
      elif params['class'] == -1:
        for i in range(0,10):
	        filterdict['c'+str(i)] = 0
      else:
        filterdict['c'+str(params['class'])] = 1
      outlist['data'] = await self.gettrainimages(filterdict)
      if settings.DEBUG:
        print('-->', outlist)
      await self.send(json.dumps(outlist))

    elif params['command'] == 'gettags':

      outlist['data'] = await self.gettags(params['school'])
      if settings.DEBUG:
        print('-->', outlist)
      await self.send(json.dumps(outlist))

    elif params['command'] == 'getpredictions':
      imglist = await self.getimagelist(params['idxs'], params['is_school'])
      count = imglist.shape[0] // self.maxblock
      rest = imglist.shape[0] % self.maxblock
      predictions = np.empty((0, len(classes_list)), np.float32)
      if count > 0:
        for i in range(count):
          if i == 0:
            myslice = imglist[:self.maxblock]
          else:
            myslice = imglist[(i * self.maxblock):((i+1) * self.maxblock)]
          tfworker.users[self.tf_w_index].fifoin.put([params['school'], myslice])
          myoutput = tfworker.users[self.tf_w_index].fifoout.get()
          predictions = np.append(predictions, myoutput, 0)
      if rest > 0:
        myslice = imglist[(count * self.maxblock):]
        tfworker.users[self.tf_w_index].fifoin.put([params['school'], myslice])
        myoutput =  tfworker.users[self.tf_w_index].fifoout.get()
        predictions = np.append(predictions, myoutput, 0)
      outlist['data'] = predictions.tolist()
      if settings.DEBUG:
        print('-->', outlist)
      await self.send(json.dumps(outlist))

    elif params['command'] == 'deltrainframe':
      outlist['data'] = await self.deltrainframe(params['idx'])
      if settings.DEBUG:
        print('-->', outlist)
      await self.send(json.dumps(outlist))

    elif params['command'] == 'checkall':
      filterdict = {'school' : params['model']}
      if params['class'] == -2:
        pass
      elif params['class'] == -1:
        for i in range(0,len(classes_list)):
	        filterdict['c'+str(i)] = 0
      else:
        filterdict['c'+str(params['class'])] = 1
      outlist['data'] = await self.checkall(filterdict)
      if settings.DEBUG:
        print('-->', outlist)
      await self.send(json.dumps(outlist))

    elif params['command'] == 'deleteall':
      filterdict = {'school' : params['model']}
      if params['class'] == -2:
        pass
      elif params['class'] == -1:
        for i in range(0,10):
	        filterdict['c'+str(i)] = 0
      else:
        filterdict['c'+str(params['class'])] = 1
      filterdict['checked'] = 1
      outlist['data'] = await self.deleteall(filterdict)
      if settings.DEBUG:
        print('-->', outlist)
      await self.send(json.dumps(outlist))

    elif params['command'] == 'register_ai':
      self.xdim = djconf.getconfigint('tr_xdim', 331)
      self.ydim = djconf.getconfigint('tr_ydim', 331)
      self.tf_w_index = tfworker.register()
      outlist['data'] = 'OK'
      if settings.DEBUG:
        print('-->', outlist)
      await self.send(json.dumps(outlist))

#*****************************************************************************
# SchoolDBUtilConsumer
#*****************************************************************************

class SchoolDBUtilConsumer(AsyncWebsocketConsumer):

  @database_sync_to_async
  def getschoolframes(self, myevent, dolock):
    if (dolock == '1'):
      is_locked = True
      with transaction.atomic():
        try:
          dbline = event.objects.get(id=myevent)
          if (dbline.userlock == None) or (dbline.userlock.id == self.usernr):
            setattr(dbline, 'userlock_id', self.usernr)
            setattr(dbline, 'locktime', timezone.now())
            dbline.save()
            is_locked = False	
        except event.DoesNotExist:
          pass
    else:
      is_locked = False
    if is_locked:
      return('Locked')
    else:
      framelines = event_frame.objects.filter(event__id=myevent)
      framelines = [item for item in framelines if os.path.isfile(
        djconf.getconfig('schoolframespath')+item.name)]
      return(serializers.serialize('json', framelines, fields=('name', 'time')))

  @database_sync_to_async
  def settags(self, params):
    eventline = event.objects.get(id=params['event'])
    mymodel = eventline.school
    modelpath = mymodel.dir
    if access.check('S', mymodel.id, self.scope['user'], 'W'):
      framelines = event_frame.objects.filter(event__id = params['event'])
      i = 0
      for item in framelines:
        newname = 'frames/'+item.name.split('/')[2]
        if item.status == -1:
          t = trainframe.objects.get(id=item.trainframe)
          newitem = False
        else:
          move(djconf.getconfig('schoolframespath') + item.name,
            modelpath + newname)
          t = trainframe(made=item.time,
            school=mymodel.id,
            name=newname,
            code='NE',
            checked=0,
            made_by_id=self.usernr,
          );
          newitem = True
        t.c0=params['cblist'][i][0]
        t.c1=params['cblist'][i][1]
        t.c2=params['cblist'][i][2]
        t.c3=params['cblist'][i][3]
        t.c4=params['cblist'][i][4]
        t.c5=params['cblist'][i][5]
        t.c6=params['cblist'][i][6]
        t.c7=params['cblist'][i][7]
        t.c8=params['cblist'][i][8]
        t.c9=params['cblist'][i][9]
        t.save()
        item.status = -1
        item.trainframe = trainframe.objects.latest('id').id
        item.save()
        i += 1
      eventline.done = True
      eventline.save()
      try:
        infoline = userinfo.objects.get(user__id=self.usernr)
      except userinfo.DoesNotExist:
        infoline = None
    else:
      infoline = None
    if infoline is not None:
      if newitem:
        infoline.counter += 1
        infoline.save()
    return('OK')

  @database_sync_to_async
  def removelocks(self):
    event.objects.filter(userlock_id=self.usernr).update(userlock_id=None)

  @database_sync_to_async
  def delevent(self, myevent):
    eventline = event.objects.get(id=myevent)
    mymodel = eventline.school
    if access.check('S', mymodel.id, self.scope['user'], 'W'):
      event_frame.objects.filter(event_id=myevent).delete()
      event.objects.get(id=myevent).delete()

  async def connect(self):
    if self.scope['user'].is_authenticated:
      self.usernr = self.scope['user'].id
      await self.accept()
    else:
      await self.close()

  async def disconnect(self, close_code):
    await self.removelocks()


  async def receive(self, text_data):
    if settings.DEBUG:
      print('<--', text_data)
    params = json.loads(text_data)['data']
    outlist = {'tracker' : json.loads(text_data)['tracker']}

    if params['command'] == 'getschoolframes':
      outlist['data'] = await self.getschoolframes(params['event'], params['dolock'])
      if settings.DEBUG:
        print('-->', outlist)
      await self.send(json.dumps(outlist))

    if params['command'] == 'settags':
      outlist['data'] = await self.settags(params)
      if settings.DEBUG:
        print('-->', outlist)
      await self.send(json.dumps(outlist))		

    if params['command'] == 'delevent':
      if settings.DEBUG:
        print('-->', outlist)
      await self.delevent(params['event'])
      outlist['data'] = 'OK'
      await self.send(json.dumps(outlist))		

#*****************************************************************************
# triggerConsumer
#*****************************************************************************

class triggerConsumer(WebsocketConsumer):

  def connect(self):
    self.viewdict = {} 
    self.loglist = []
    self.accept()

  def send_trigger(self, viewnr):
    try:
      self.send('T'+str(viewnr))
    except Disconnected:
      print('*** Could not send Trigger, socket closed...')


  def disconnect(self, close_code):
    for v_item in self.viewdict:
      view_item = c_base.instances['V'][v_item]
      view_item.inbuffer.pop_from_onf(self.viewdict[v_item])
      view_item.minus_1()
    self.triggeractive = False
    for item in self.loglist:
      item.stop = timezone.now()
      item.active = False
      item.save()


  def receive(self, text_data):
    if settings.DEBUG:
      print('<--', text_data)
    params = json.loads(text_data)['data']
    outlist = {'tracker' : json.loads(text_data)['tracker']}
    if params['command'] == 'starttrigger':
      view_item = c_base.instances['V'][params['viewnr']]
      if access.check(view_item.params['source_type'], view_item.params['source_id'], self.scope['user'], 'R'):
        def onf():
          self.send_trigger(params['viewnr'])
        index = view_item.inbuffer.push_to_onf(onf)
        self.viewdict[params['viewnr']] = index
        view_item.plus_1()
        if self.scope['user'].is_authenticated:
          myuser = self.scope['user'].id
        else:
          myuser = -1
        my_log_line = view_log(v_type=view_item.params['source_type'],
          v_id=view_item.params['source_id'],
          start=timezone.now(),
          stop=timezone.now(),
          user=myuser,
          active=True,
        )
        my_log_line.save()
        self.loglist.append(my_log_line)
        outlist['data'] = 'OK'
      else:
        self.close()
    if settings.DEBUG:
      print('-->', outlist)
    self.send(json.dumps(outlist))

#*****************************************************************************
# c_viewConsumer
#*****************************************************************************

class c_viewConsumer(AsyncWebsocketConsumer):

  async def connect(self):
    await self.accept()

  async def receive(self, text_data):
    if settings.DEBUG:
      print('<--', text_data)
    params = json.loads(text_data)['data']
    outlist = {'tracker' : json.loads(text_data)['tracker']}

    if params['command'] == 'getcaminfo':
      view_item = c_base.instances['V'][params['viewnr']]
      if access.check(view_item.params['source_type'], view_item.params['source_id'], self.scope['user'], 'R'):
        myparent = view_item.parent
        outlist['data'] = {}
        outlist['data']['fps'] = round(myparent.params['fpsactual'], 2)
        outlist['data']['viewers'] = myparent.view_count
        if settings.DEBUG:
          print('-->', outlist)
        try:
          await self.send(json.dumps(outlist))	
        except Disconnected:
          print('*** Could not send Cam Info , socket closed...')
      else:
        await self.close()

		

#*****************************************************************************
# oneitemConsumer
#*****************************************************************************

class oneitemConsumer(AsyncWebsocketConsumer):

  @database_sync_to_async
  def mouseuphandler(self, x, y):
	  self.myitem.view_object.mouseuphandler(x, y)
	  return()

  @database_sync_to_async
  def setapplymask(self, value):
	  self.myitem.setparams({'apply_mask' : value}, writedb=True)
	  return()

  @database_sync_to_async
  def deletecondition(self, number):
	  evt_condition.objects.get(id=number).delete()
	  return()

  @database_sync_to_async
  def getcondition(self, number):
	  return(evt_condition.objects.get(id=number))

  @database_sync_to_async
  def savecondition(self, number, c_type, x, y):
	  with transaction.atomic():
		  dbline = evt_condition.objects.get(id=number)	
		  setattr(dbline, 'c_type', c_type)
		  setattr(dbline, 'x', x)
		  setattr(dbline, 'y', y)
		  dbline.save()

  @database_sync_to_async
  def newcondition(self, and_or, reaction):
	  with transaction.atomic():
		  dbline = evt_condition(and_or=and_or, reaction=reaction, 
        eventer_id=self.myitem.id)
		  dbline.save()
		  newid =  evt_condition.objects.latest('id').id
	  dbline = evt_condition.objects.get(id=newid)
	  return(model_to_dict(dbline))

  async def connect(self):
    await self.accept()
    self.myitem = None

  async def disconnect(self, close_code):
    if self.myitem is not None:
      self.myitem.nr_of_cond_ed = 0
      self.myitem.last_cond_ed = 0

  async def receive(self, text_data):
    if settings.DEBUG:
      print('<--', text_data)
    params = json.loads(text_data)['data']
    outlist = {'tracker' : json.loads(text_data)['tracker']}

    if params['command'] == 'setmyitem':
      if access.check(params['mode'], params['itemid'], self.scope['user'], 'R'):
        self.myitem = c_base.instances[params['mode']][int(params['itemid'])]
        self.may_write = access.check(params['mode'], int(params['itemid']), self.scope['user'], 'W')
        outlist['data'] = 'OK'
        if settings.DEBUG:
	        print('-->', outlist)
        await self.send(json.dumps(outlist))	
      else:
        await self.close()

    elif params['command'] == 'setonefield':
      if self.may_write:
        if type(self.myitem.params[params['pname']]) == int:
	        self.myitem.params[params['pname']] = int(params['value'])
        elif type(self.myitem.params[params['pname']]) == float:
	        self.myitem.params[params['pname']] = float(params['value'])
        else:
	        self.myitem.params[params['pname']] = params['value']
      outlist['data'] = 'OK'
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))	

    elif params['command'] == 'setcbstatus':
      if self.may_write:
        if 'ch_show' in params:
	        self.myitem.view_object.showmask = params['ch_show']
        if 'ch_edit' in params:
	        self.myitem.view_object.editmask = params['ch_edit']
        if 'ch_apply' in params:
	        await self.setapplymask(params['ch_apply'])
        if 'ch_white' in params:
	        self.myitem.view_object.whitemarks = params['ch_white']
      outlist['data'] = 'OK'
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))	

    elif params['command'] == 'setbtevent':
      if self.may_write:
        if 'bt_new' in params:
	        self.myitem.view_object.make_new_ring()
	        self.myitem.view_object.feed_back()
	        self.myitem.view_object.refresh_mask()
	        self.myitem.view_object.refresh_drawing()
      outlist['data'] = 'OK'
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))	

    elif params['command'] == 'mousedown':
      if self.may_write:
        self.myitem.view_object.mousedownhandler(params['x'], params['y'])
      outlist['data'] = 'OK'
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))	

    elif params['command'] == 'mouseup':
      if self.may_write:
       await self.mouseuphandler(params['x'], params['y'])
      outlist['data'] = 'OK'
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))	

    elif params['command'] == 'mousemove':
      if self.may_write:
        self.myitem.view_object.mousemovehandler(params['x'], params['y'])
      outlist['data'] = 'OK'
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))	

    elif params['command'] == 'delcondition':
      if self.may_write:
        await self.deletecondition(params['c_nr'])
        self.myitem.cond_dict[params['reaction']] = [item 
          for item in self.myitem.cond_dict[params['reaction']] 
          if str(item['id'])!=params['c_nr']]
        self.myitem.set_cam_counts()
      outlist['data'] = 'OK'
      if settings.DEBUG:
         print('-->', outlist)
      await self.send(json.dumps(outlist))		

    elif params['command'] == 'getcondition':
      if self.may_write:
        mydata = await self.getcondition(params['c_nr'])
      outlist['data'] = model_to_dict(mydata, exclude=[])
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))		

    elif params['command'] == 'cond_ed_plus1':
      if self.may_write:
        self.myitem.last_cond_ed = int(params['reaction'])
        self.myitem.nr_of_cond_ed += 1
      outlist['data'] = 'OK'
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))		

    elif params['command'] == 'cond_ed_minus1':
      if self.may_write:
        self.myitem.nr_of_cond_ed = max(0, self.myitem.nr_of_cond_ed - 1)
      outlist['data'] = 'OK'
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))		

    elif params['command'] == 'get_all_conditions':
      outlist['data'] = self.myitem.cond_dict
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))		

    elif params['command'] == 'cond_to_str':
      outlist['data'] = self.myitem.build_string(params['condition'])
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))		

    elif params['command'] == 'savecondition':
      if self.may_write:
        for item in self.myitem.cond_dict[params['reaction']]:
	        if str(item['id']) == params['c_nr']:
		        item['c_type'] = int(params['c_type'])
		        item['x'] = int(params['x'])
		        item['y'] = float(params['y'])
		        break
        self.myitem.set_cam_counts()
        if params['save_db']:
	        await self.savecondition(params['c_nr'], int(params['c_type']), 
            int(params['x']), float(params['y']))
      outlist['data'] = 'OK'
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))		

    elif params['command'] == 'newcondition':
      newitem = await self.newcondition(int(params['and_or']), 
        int(params['reaction']))
      if self.may_write:
        self.myitem.cond_dict[params['reaction']].append(newitem)
        self.myitem.set_cam_counts()
      outlist['data'] = newitem
      if settings.DEBUG:
	      print('-->', outlist)
      await self.send(json.dumps(outlist))	

#*****************************************************************************
# repeaterConsumer
#*****************************************************************************

class repeaterConsumer(WebsocketConsumer):

  register = {}

  def connect(self):
    self.rep_id = None
    self.password = None
    self.host_register_complete = False
    self.accept()
    self.ffprobe_urls = {}

  def disconnect(self, close_code):
    del repeaterConsumer.register[self.rep_id]
    self.password = None
    self.host_register_complete = False
    

  def receive(self, text_data=None, bytes_data=None):
    #print('--->', text_data)
    command = text_data[:7]
    params = text_data[7:]
    if command == 'rep_id:':
      self.rep_id = int(params)
      self.send('OK')
    elif command == 'passwo:':
      self.password = params
      my_repeater = repeater.objects.get(id=self.rep_id)
      storage = bytes.fromhex(my_repeater.password)
      salt = storage[:32]
      key = storage[32:]
      new_key = pbkdf2_hmac(
        'sha256', self.password.encode('utf-8'),
        salt, 100000
      )
      if new_key != key:
        self.close()
      else:
        if not (self.rep_id in repeaterConsumer.register):
          repeaterConsumer.register[self.rep_id] = {}
          repeaterConsumer.register[self.rep_id]['fifos'] = {}
        if not ('myself' in repeaterConsumer.register[self.rep_id]):
          repeaterConsumer.register[self.rep_id]['myself'] = self
        self.host_register_complete = True
        repeaterConsumer.register[self.rep_id]['token'] = str(randint(0,999999)).zfill(6)
        self.send('token_:'+repeaterConsumer.register[self.rep_id]['token'])
    elif command == 'ticker:':
      pass
    elif command == 'ipitem:':
      params = json.loads(params)
    elif command == 'ipdone:':
      self.host_register_complete = True
    elif command == 'ffpres:':
      params = json.loads(params)
      self.ffprobe_urls[params[0]] = params[1]

  def get_rep_cam_nr(self):
    count = 1
    while count in repeaterConsumer.register[self.rep_id]['fifos']:
      count += 1
    return(count)

  def rep_connect(self, url, count):
    print('Repeater', self.rep_id, 'Connecting Url', url)
    if not os.path.exists('c_client/fifo'):
      os.mkdir('c_client/fifo')
    self.fifoname = 'c_client/fifo/rep_fifo_'+str(self.rep_id)+'_'+str(count)
    if os.path.exists(self.fifoname):
      os.remove(self.fifoname)
    os.mkfifo(self.fifoname)
    repeaterConsumer.register[self.rep_id]['fifos'][count] = open('c_client/fifo/rep_fifo_'+str(self.rep_id)+'_'+str(count), 'wb')
    self.send('hostco:'+json.dumps((count, url)))
    return(count)

  def probe(self, url):
    self.ffprobe_urls[url] = None
    self.send('ffprob:'+url)
    while self.ffprobe_urls[url] is None:
      sleep(1)
    return(self.ffprobe_urls[url])
    
      
#*****************************************************************************
# repeaterCamConsumer
#*****************************************************************************

class repeaterCamConsumer(WebsocketConsumer):

  def connect(self):
    self.accept()
    #self.count = 0

  def receive(self, text_data=None, bytes_data=None):
    #self.count += 1
    #print('++++++++++', str(self.count))
    rep_nr = int(bytes_data[:6].decode())
    bytes_data = bytes_data[6:]
    cam_nr = int(bytes_data[:6].decode())
    bytes_data = bytes_data[6:]
    if bytes_data[:6].decode() == repeaterConsumer.register[rep_nr]['token']:
      bytes_data = bytes_data[6:]
      repeaterConsumer.register[rep_nr]['fifos'][cam_nr].write(bytes_data)
      repeaterConsumer.register[rep_nr]['fifos'][cam_nr].flush
    else:
      self.close()
    #print('----------', str(self.count))
    self.send('readyr:')
    
      
#*****************************************************************************
# predictionsConsumer
#*****************************************************************************

class predictionsConsumer(WebsocketConsumer):

  def connect(self):
    self.tf_w_index = tfworker.register()
    self.accept()
    self.authed = False
    self.permitted_schools = set()
    self.user = None

  def receive(self, text_data=None, bytes_data=None):
    indict=json.loads(zlib.decompress(bytes_data))
    if indict['code'] == 'imgl':
      if not self.authed:
        self.close()
      if not (indict['scho'] in self.permitted_schools):
        if access.check('S', indict['scho'], self.user, 'R'):
          self.permitted_schools.add(indict['scho'])
          #print('Access approved')
        else:
          #print('Access not approved')
          self.close()
      imglist = np.array(indict['data'])
      tfworker.users[self.tf_w_index].fifoin.put([indict['scho'], imglist])
      predictions = tfworker.users[self.tf_w_index].fifoout.get().tolist()
      self.send(json.dumps(predictions))
    elif indict['code'] == 'auth':
      print(indict)
      self.user = User.objects.get(username=indict['name'])
      if self.user.check_password(indict['pass']):
        self.authed = True
        #print('Success')
      if not self.authed:
        self.close()
        #print('No success')

  def disconnect(self, close_code):
    tfworker.unregister(self.tf_w_index)


