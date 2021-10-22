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

from concurrent import futures
from PIL import Image
from time import sleep
from json import loads
from logging import getLogger
import cv2 as cv
import requests
import numpy as np
import ffmpeg
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.conf import settings
from django.core import serializers
from django.shortcuts import render
from .models import tag, userinfo, event, event_frame, trainframe, fit, epoch, view, cam, detector, eventer, school
from .forms import CamForm, DetectorForm, EventerForm, CamTestForm
from .l_tools import update_from_dict
from .c_tools import djconf, run_with_log
from .c_base import c_base
from .c_cam import c_cam
from .c_buffer import c_buffer
from .c_view import c_view
from .c_detector import c_detector
from .c_eventer import c_eventer
from .c_convert import c_convert
from .c_access import access
from .c_tfworker import tfworker
from .c_schools import get_taglist
from .c_stream_clients import c_stream_dict

#mystreams = c_stream_dict()

executor = futures.ThreadPoolExecutor(max_workers=1000)

skipinit = False

#Migrating the Database:
#
#skipinit = True

if skipinit:
  print('***** Initialization in views.py disabled ! *****')
else:
  items_to_start = []
  items_to_postinit = []

  items_to_start.append((tfworker.run1, 'tfworker1'))	
  items_to_start.append((tfworker.run2, 'tfworker2'))	
  
  for line in cam.objects.filter(active=True):
    mycam = c_cam(line.id)
    items_to_start.append((mycam.run, 'camera_'+str(line.id)))	
    items_to_postinit.append(mycam.postinit)

  for line in detector.objects.filter(active=True):
    mydetector = c_detector(line.id)
    items_to_start.append((mydetector.run, 'detector_'+str(line.id)))
    items_to_postinit.append(mydetector.postinit)

  for line in eventer.objects.filter(active=True):
    myeventer = c_eventer(line.id)	
    items_to_start.append((myeventer.run, 'eventer_'+str(line.id)))	
    items_to_start.append((myeventer.detected_frames, 
      'e_inserter_'+str(line.id)))	
    items_to_postinit.append(myeventer.postinit)

  for line in view.objects.filter(active=True):
    myview = c_view(line.id)	
    items_to_postinit.append(myview.postinit)

  for item in items_to_postinit:
    item()

  for item in items_to_start:   
    run_with_log(executor, item[0], item[1])

@login_required
def logout_view(request):
	logout(request)
	return(HttpResponse('Logged Out...'))

@login_required
def cam_index(request):
  for camline in cam.objects.filter(active=True):
    mycam = c_base.instances['C'][camline.id]
    mycam.view_object.setviewsize('S')
  template = loader.get_template('c_client/index.html')
  viewlist = access.filter_views(view.objects.filter(active=True), request.user, 'R')
  schoollist = access.filter_schools(school.objects.filter(active=True), request.user, 'R')
  context = {'debug' : settings.DEBUG,
    'mode' : 'C',
    'c_views' : viewlist,
    'c_schools' : schoollist,
    'sizecode' : 'S',
    'user' : request.user,
  }
  return(HttpResponse(template.render(context)))

def onecam(request, camnr):
  if access.check('C', camnr, request.user, 'R'):
    mycamline = cam.objects.get(id=camnr)
    mycam = c_base.instances['C'][camnr]
    mycam.view_object.setviewsize('L')
    myurl = '/c_client/onecam/'
    if request.method == 'POST':
      form = CamForm(request.POST)
      if form.is_valid():
        mycam.setparams(form.cleaned_data, writedb=True)
        return HttpResponseRedirect(myurl+str(camnr)+'/')
    else:
      outbuffers = loads(mycamline.outbuffers)
      viewnr = 0
      for ob in outbuffers:
        if ob[0] == 'V':
          viewnr = ob[1]
          break
      form = CamForm(initial={
        'url_img' : mycamline.url_img,
        'url_vid' : mycamline.url_vid,
        'url_vid' : mycamline.url_vid,
        'feed_type' : mycamline.feed_type,
        'fpslimit' : mycamline.fpslimit,
      })
      viewlist = access.filter_views(view.objects.filter(active=True), request.user, 'R')
      schoollist = access.filter_schools(school.objects.filter(active=True), request.user, 'R')
      context = {
        'debug' : settings.DEBUG,
        'mode' : 'C',
        'myitem' : mycamline,
        'c_view' : view.objects.get(id=viewnr),
        'c_views' : viewlist,
        'c_schools' : schoollist,
        'myurl' : myurl,
        'form' : form,
        'sizecode' : 'L',
        'may_write' : access.check('C', camnr, request.user, 'W'),
        'user' : request.user,
      }
    return(render(request, 'c_client/oneitem.html', context))
  else:
    return(HttpResponse('No Access'))

@login_required
def detector_index(request):
  for detectorline in detector.objects.filter(active=True):
    mydetector = c_base.instances['D'][detectorline.id]
    mydetector.view_object.setviewsize('S')
  template = loader.get_template('c_client/index.html')
  viewlist = access.filter_views(view.objects.filter(active=True), request.user, 'R')
  schoollist = access.filter_schools(school.objects.filter(active=True), request.user, 'R')
  context = {'debug' : settings.DEBUG,
    'mode' : 'D',
    'c_views' : viewlist,
    'c_schools' : schoollist,
    'user' : request.user,
  }
  return(HttpResponse(template.render(context)))

def onedetector(request, detectornr):
  if access.check('D', detectornr, request.user, 'R'):
    mydetectorline = detector.objects.get(id=detectornr)
    mydetector = c_base.instances['D'][detectornr]
    mydetector.view_object.setviewsize('L')
    myurl = '/c_client/onedetector/'
    if request.method == 'POST':
      form = DetectorForm(request.POST)
      if form.is_valid():
        mydetector.setparams(form.cleaned_data, writedb=True)
        return HttpResponseRedirect(myurl+str(detectornr)+'/')
    else:
      outbuffers = loads(mydetectorline.outbuffers)
      viewnr = 0
      for ob in outbuffers:
        if ob[0] == 'V':
          viewnr = ob[1]
          break
      form = DetectorForm(initial={
        'backgr_delay' : mydetectorline.backgr_delay,
        'dilation' : mydetectorline.dilation,
        'erosion' : mydetectorline.erosion,
        'max_size' : mydetectorline.max_size,
        'threshold' : mydetectorline.threshold,
        'max_rect' : mydetectorline.max_rect,
      })
      viewlist = access.filter_views(view.objects.filter(active=True), request.user, 'R')
      schoollist = access.filter_schools(school.objects.filter(active=True), request.user, 'R')
      context = {'debug' : settings.DEBUG,
        'mode' : 'D',
        'myitem' : mydetectorline,
        'c_view' : view.objects.get(id=viewnr),
        'c_views' : viewlist,
        'c_schools' : schoollist,
        'myurl' : myurl,
        'form' : form,
        'may_write' : access.check('D', detectornr, request.user, 'W'),
        'user' : request.user,
      }
    return render(request, 'c_client/oneitem.html', context)
  else:
    return(HttpResponse('No Access'))

@login_required
def eventer_index(request):
  for eventerline in eventer.objects.filter(active=True):
    myeventer = c_base.instances['E'][eventerline.id]
    myeventer.view_object.setviewsize('S')
  template = loader.get_template('c_client/index.html')
  viewlist = access.filter_views(view.objects.filter(active=True), request.user, 'R')
  schoollist = access.filter_schools(school.objects.filter(active=True), request.user, 'R')
  context = {'debug' : settings.DEBUG,
    'mode' : 'E',
    'c_views' : viewlist,
    'c_schools' : schoollist,
    'user' : request.user,
  }
  return(HttpResponse(template.render(context)))

def oneeventer(request, eventernr):
  print(request.user)
  if access.check('E', eventernr, request.user, 'R'):
    myeventerline = eventer.objects.get(id=eventernr)
    myeventer = c_base.instances['E'][eventernr]
    myeventer.view_object.setviewsize('L')
    myurl = '/c_client/oneeventer/'
    if request.method == 'POST':
      form = EventerForm(request.POST)
      if form.is_valid():
        myeventer.setparams(form.cleaned_data, writedb=True)
        return HttpResponseRedirect(myurl+str(eventernr)+'/')
    else:
      outbuffers = loads(myeventerline.outbuffers)
      viewnr = 0
      for ob in outbuffers:
        if ob[0] == 'V':
          viewnr = ob[1]
          break
      form = EventerForm(initial={
        'margin' : myeventerline.margin,
        'event_time_gap' : myeventerline.event_time_gap,
        'school' : myeventerline.school,
        'alarm_email' : myeventerline.alarm_email,
      })
      viewlist = access.filter_views(view.objects.filter(active=True), request.user, 'R')
      schoollist = access.filter_schools(school.objects.filter(active=True), request.user, 'R')
      context = {'debug' : settings.DEBUG,
        'mode' : 'E',
        'myitem' : myeventer,
        'myschool' : myeventerline.school,
        'c_view' : view.objects.get(id=viewnr),
        'c_views' : viewlist,
        'c_schools' : schoollist,
        'myurl' : myurl,
        'form' : form,
        'may_write' : access.check('E', eventernr, request.user, 'W'),
        'user' : request.user,
      }
    return render(request, 'c_client/oneitem.html', context)
  else:
    return(HttpResponse('No Access'))


@login_required
def check(request):
  template = loader.get_template('c_client/check.html')
  context = {'c_views' : access.filter_views(view.objects.filter(active=True), request.user, 'R'),
    'c_schools' : access.filter_schools(school.objects.filter(active=True), request.user, 'R'),
    'c_schools_write' : access.filter_schools(school.objects.filter(active=True), request.user, 'W'),
    'user' : request.user,
    'debug' : settings.DEBUG,
    'user' : request.user,
  }
  return(HttpResponse(template.render(context)))

@login_required
def oneschool(request, schoolnr):
  if access.check('S', schoolnr, request.user, 'R'):
    template = loader.get_template('c_client/oneschool.html')
    viewlist = access.filter_views(view.objects.filter(active=True), request.user, 'R')
    schoollist = access.filter_schools(school.objects.filter(active=True), request.user, 'R')
    try:
      myuserinfo = userinfo.objects.get(user = request.user.id)
    except userinfo.DoesNotExist:
      myuserinfo = userinfo(user_id=request.user.id, school_id=schoolnr, counter=0)
    context = {'userinfo' : myuserinfo,
	    'user' : request.user,
      'c_school' : school.objects.get(id=schoolnr),
      'c_views' : viewlist,
      'c_schools' : schoollist,
      'events' : (event.objects.filter(school = schoolnr, userlock_id = None, done = False, xmax__gt = 0) 
        | event.objects.filter(school = schoolnr, userlock_id = request.user.id, done = False, xmax__gt = 0)),
      'debug' : settings.DEBUG,
      'may_write' : access.check('S', schoolnr, request.user, 'W'),
      'user' : request.user,
    }
    return(HttpResponse(template.render(context)))
  else:
    return(HttpResponse('No Access'))

@login_required
def stats(request):
	package = []
	for myschool in school.objects.all():
		item = {'name' : myschool.name,
			'modelfits' : fit.objects.filter(school=myschool.id),
			'count' : trainframe.objects.filter(school=myschool.id).count(),
			'id' : myschool.id,
		}
		package.append(item)
	template = loader.get_template('c_client/stats.html')
	context = {'debug' : settings.DEBUG,
		'schools' : package,
	}
	return(HttpResponse(template.render(context)))

@login_required
def statdetails(request, fitnr):
	description = fit.objects.get(id=fitnr).description.splitlines()
	template = loader.get_template('c_client/statdetails.html')
	context = {'debug' : settings.DEBUG,
		'epochs' : epoch.objects.filter(fit=fitnr),
		'fitnr' : fitnr,
		'description' : description,
	}
	return(HttpResponse(template.render(context)))

#@login_required
def getbmp(request, model, name): #model = 0 --> school
  if model == 0:
    name = name.replace('$', '/', 2)
    filepath = djconf.getconfig('schoolframespath') + name
  else:
    line = school.objects.get(id=model)
    filepath = line.dir + 'frames/' + name
  try:
    with open(filepath, "rb") as f:
      return HttpResponse(f.read(), content_type="image/jpeg")
  except IOError:
    red = Image.new('RGB', (1, 1), (255,0,0))
    response = HttpResponse(content_type="image/jpeg")
    red.save(response, "JPEG")
    return response

#@login_required
def getmp4(request, name):
  filepath = djconf.getconfig('recordingspath') + name
  try:
    with open(filepath, "rb") as f:
      return HttpResponse(f.read(), content_type="video/mp4")
  except IOError:
    red = Image.new('RGB', (100, 100), (255,0,0))
    response = HttpResponse(content_type="image/jpeg")
    red.save(response, "JPEG")
    return response

def getjpg(request, c_id, counter):
  myview = c_view.instances['V'][c_id]
  if access.check(myview.params['source_type'], myview.params['source_id'], request.user, 'R'):
    frame = myview.inbuffer.getframeonly()
    frame = c_convert(frame, typein=3, xout=myview.xview, 
      yout=myview.yview)
    if myview.showmask and (myview.img_add is not None):
      frame = cv.addWeighted(frame, 1, (255-myview.img_add), -0.3, 0)
    if myview.editmask and (myview.drawpad is not None):
      if myview.whitemarks:
        frame = cv.addWeighted(frame, 1, (255-myview.drawpad), 1, 0)
      else:
        frame = cv.addWeighted(frame, 1, (255-myview.drawpad), -1.0, 0)
    frame = c_convert(frame, typein=3, typeout=1)
    return HttpResponse(frame, content_type="image/jpeg")
  else:
    return(HttpResponse('No Access'))

def c_canvas(request, c_viewnr, mode, idx):
  myview = c_view.instances['V'][c_viewnr]
  if access.check(myview.params['source_type'], myview.params['source_id'], request.user, 'R'):
    if request.user.is_authenticated:
      name_to_use = myview.params['name']
    else:
      name_to_use = 'This ist realtime.'
    context = {
      'vidx' : c_viewnr,
      'name' : name_to_use,
      'xres' : myview.params['xres'],
      'yres' : myview.params['yres'],
      'width' : myview.xview,
      'height' : myview.yview,
      'mode' : mode,
      'idx' : idx,
    }
    template = loader.get_template('c_client/c_canvas.html')
    return(HttpResponse(template.render(context)))
  else:
    return(HttpResponse('No Access'))

@login_required
def camtest(request):
  viewlist = access.filter_views(view.objects.filter(active=True), request.user, 'R')
  schoollist = access.filter_schools(school.objects.filter(active=True), request.user, 'R')
  camlist = access.filter_cams(cam.objects.filter(active=True), request.user, 'R')
  context = {
    'debug' : settings.DEBUG,
    'form' : CamTestForm(),
    'url' : '',
    'c_views' : viewlist,
    'c_schools' : schoollist,
    'cams' : camlist,
    'v_index' : 0,
    'user' : request.user,
  }
  if request.method == 'POST':
    form = CamTestForm(request.POST)
    if form.is_valid():
      url = form.cleaned_data['url']
      f_type = form.cleaned_data['feed_type']
      mycam = c_cam(0, int(f_type))
      mycam.params['repeater'] = 0
      if mycam.params['feed_type'] in {2, 3}:
        mycam.params['url_vid'] = url
      elif  mycam.params['feed_type'] == 1:
        mycam.params['url_img'] = url
      run_with_log(None, mycam.set_x_y, 'camera_0')
      if mycam.online > 0:
        mycam.params['feed_type'] = int(f_type)
        mycam.params['apply_mask'] = 0
        mycam.params['fpslimit'] = 25
        mycam.params['fpsactual'] = 0
        myview = c_view(0)
        myview.params['xres'] = mycam.params['xres']
        myview.params['yres'] = mycam.params['yres']
        myview.params['name'] = 'Testing...'
        mycam.children = [myview]
        myview.parent = mycam
        myview.setviewsize('L')
        context ['url'] = url
        context['v_index'] = myview.v_index
        run_with_log(executor, mycam.run, 'camera_0')
  template = loader.get_template('c_client/camtest.html')
  return render(request, 'c_client/camtest.html', context)

@login_required
def eventlist(request, schoolnr):
  if access.check('S', schoolnr, request.user, 'R'):
    event_set = set()
    template = loader.get_template('c_client/eventlist.html')
    viewlist = access.filter_views(view.objects.filter(active=True), request.user, 'R')
    schoollist = access.filter_schools(school.objects.filter(active=True), request.user, 'R')
    try:
      myuserinfo = userinfo.objects.get(user = request.user.id)
    except userinfo.DoesNotExist:
      myuserinfo = userinfo(user_id=request.user.id, school_id=schoolnr, counter=0)
    context = {'c_school' : school.objects.get(id=schoolnr),
      'c_views' : viewlist,
      'c_schools' : schoollist,
      'events' : event.objects.filter(school = schoolnr).exclude(videoclip='').exclude(double=True).order_by('-id'),
      'recordingsurl' : djconf.getconfig('recordingsurl'),
      'debug' : settings.DEBUG,
      'may_write' : access.check('S', schoolnr, request.user, 'W'),
      'user' : request.user,
    }
    return(HttpResponse(template.render(context)))
  else:
    return(HttpResponse('No Access'))
