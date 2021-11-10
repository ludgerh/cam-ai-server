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

from PIL import Image
from time import sleep, time
from json import loads
from os import (remove, path, mkfifo, open as fifoopen, O_RDONLY, O_NONBLOCK, 
  read as fiforead, mkdir) 
from shutil import move
from threading import Lock
from glob import glob
import json
from subprocess import Popen, PIPE, DEVNULL
import cv2 as cv
import requests
import numpy as np
import ffmpeg
import multitimer
from django.utils import timezone
from .models import cam, mask
from .l_tools import ts2filename
from .c_tools import djconf
from .c_device import c_device
from .c_convert import c_convert
from .c_masks import mask_list
from .consumers import repeaterConsumer

# Feed types:
# 1 : Seperate Jpeg Frames
# 2 : Others, RTSP, RTMP and Laptop Cameras
# 3 : RTSP

class c_cam(c_device):

  def __init__(self, id=None, ft=None):
    self.modelclass = cam
    super().__init__(id, type='C')
    if ft:
      self.params['feed_type'] = ft
    if self.params['feed_type'] in {2, 3}:
      if not path.exists('c_client/fifo'):
        mkdir('c_client/fifo')
      self.fifoname = 'c_client/fifo/cam_fifo_'+str(self.id)
      if path.exists(self.fifoname):
        remove(self.fifoname)
      mkfifo(self.fifoname)
    self.mask = None
    self.int_mask_list = None
    self.online = False
    self.ff_proc_1 = None
    self.ff_proc_2 = None
    self.cam_active = False
    self.cam_ts = None
    self.vid_list = []
    self.vid_list_lock = Lock()
    self.lasttime = 0
    self.fps_counter = 0
    self.getting_newprozess = False
    self.repeater_running = False
    self.rep_cam_nr = None

  def ts_targetname(self, ts):
    return('C'+str(self.id).zfill(4)+'_'+ts2filename(ts, noblank= True)+'.mp4')

  def vid_file_path(self, nr):
    return(djconf.getconfig('recordingspath') + 'C'+str(self.id).zfill(4)
      + '_' + str(nr).zfill(8) + '.mp4')

  def latest_ready_video(self):
    with self.vid_list_lock:
      count = len(self.vid_list)
      found = False
      while count > 0:
        count -= 1
        if self.vid_list[count][3]: 
          found = True
          break
      if found:
        return(self.vid_list[count])
      else:
        return(None)

  def cleanup(self):
    new_vid_list = []
    for i in range(len(self.vid_list)):
      if self.vid_list[i][0] < (time() - 600):
        try:
          remove(djconf.getconfig('recordingspath')+self.vid_list[i][1])
        except FileNotFoundError:
          self.logger.warning('*** Delete did not find: '
            + djconf.getconfig('recordingspath') + self.vid_list[i][1])
      else:
        new_vid_list.append(self.vid_list[i])
    with self.vid_list_lock:
      self.vid_list = new_vid_list
    del new_vid_list

  def checkmp4(self):
    if self.ff_proc_2 is not None:
      if path.exists(self.vid_file_path(self.vid_count + 1)):
        if len(self.vid_list) > 1:
          self.vid_list[-2][3] = True
        timestamp = time()
        targetname = self.ts_targetname(timestamp)
        try:
          move(self.vid_file_path(self.vid_count), 
            djconf.getconfig('recordingspath')+self.vid_list[-1][1])
          self.vid_list.append([timestamp, targetname, str(self.vid_count), 
            False])
          self.vid_count += 1
        except FileNotFoundError:
          self.logger.warning(
              'Move did not find: '+self.vid_file_path(self.vid_count))
          

  def watchdog(self):
    timediff = time() - self.wd_ts
    if timediff <= 60:
      return()
    if not self.running:
      return()
    if (timediff <= 180) and (self.getting_newprozess):
      return()
    if (self.view_count == 0) and (self.data_count == 0):
      return()
    if (self.params['repeater'] > 0):
      if not self.repeater_running:
        return()
      if not self.repeater.host_register_complete:
        self.online = False
        while not self.online:
          self.set_x_y(self.logger)
          if not self.online:
            sleep(60)
    self.wd_ts = time()
    self.logger.warning('*** Wakeup for Camera #'+str(self.id))
    if self.ff_proc_1 is not None:
      self.ff_proc_1.kill()
      self.ff_proc_1 = None
    if self.ff_proc_2 is not None:
      self.ff_proc_2.kill()
      self.ff_proc_2 = None
    self.newprocess() 
    self.getting_newprozess = True
        

  def refresh_mask(self):
	  self.mask = self.int_mask_list.mask_from_polygons(
		  self.params['xres'], 
		  self.params['yres'], (255,255,255), (0,0,0)
	  )

  def newprocess(self):
    self.wd_ts = time()
    for f in glob(djconf.getconfig('recordingspath')
        + 'C' + str(self.id).zfill(4) + '_????????.mp4'):
      remove(f)
    self.clipline = None
    if self.params['feed_type'] in {2, 3}:
      inparams = '-v info -use_wallclock_as_timestamps 1'
      if self.params['feed_type'] == 3:
        inparams += ' -rtsp_transport tcp'
      outparams = ('-f rawvideo -pix_fmt bgr24 -r '
        + str(self.params['fpslimit']) + ' -vsync cfr -progress '+self.fifoname)
      if self.params['repeater'] > 0:
        self.rep_cam_nr = self.repeater.get_rep_cam_nr()
        source_string = ('c_client/fifo/rep_fifo_'
          + str(self.params['repeater']) + '_' + str(self.rep_cam_nr))
      else:
        source_string = self.params['url_vid']
      cmd = ('exec ffmpeg ' + inparams + ' -i "' + source_string + '" '
        + outparams + ' pipe:1')
      self.ff_proc_1 = Popen(cmd, stdout=PIPE, stderr=DEVNULL, shell=True)
      if self.params['repeater'] > 0:
        self.repeater.rep_connect(self.params['url_vid'], self.rep_cam_nr)
    
    if self.record_count > 0:
      self.vid_count = 0
      timestamp = time()
      self.vid_list.append([timestamp, self.ts_targetname(timestamp), 
        str(self.vid_count), False])
      inparams = {
        'v' : 'fatal',
        'format' : 'rawvideo',
        'pix_fmt' : 'bgr24',
        's' : str(self.params['xres'])+'x'+str(self.params['yres'],),
        'r' : self.params['fpslimit'],
      }
      outparams = {
        'r' : self.params['fpslimit'],
        'f' : 'segment',
        'segment_time' : 10,
        'reset_timestamps' : 1,
        'vcodec' : 'libx264',
        'x264-params' : ('keyint='+str(round(self.params['fpslimit']*10))
          + ':scenecut=0'), 
        'pix_fmt' : 'yuv420p',
        'profile:v' : 'baseline',
        'level' : 3,
      }
      filepath = (djconf.getconfig('recordingspath') + 'C'
        + str(self.id).zfill(4) + '_%08d.mp4')
      self.ff_proc_2 = (
        ffmpeg
        .input('pipe:', **inparams)
        .output(filepath, **outparams)
        .run_async(pipe_stdin=True))
    else:
      self.ff_proc_2 = None

  def set_x_y(self, mylogger):
    if self.params['feed_type'] == 1:

      self.online = False
      try:
        frame = Image.open(requests.get(self.params['url_img'], 
          stream=True).raw).convert('RGB') 
        frame = cv.cvtColor(np.array(frame), cv.COLOR_RGB2BGR)
        self.setparams({
          'xres' : frame.shape[1],
          'yres' : frame.shape[0],
        }, writedb=True)
        self.online = True
      except requests.exceptions.ReadTimeout:
        mylogger.warning('Cam #' + str(self.id)
          + ' had timeout while getting JPG')
      except requests.exceptions.ConnectTimeout:
        mylogger.warning('Cam #' + str(self.id)
          + ' had timeout while connecting for JPG')
      except requests.exceptions.ConnectionError:
        mylogger.warning('Cam #' + str(self.id)
          + ' could not connect for getting JPG')
    elif self.params['feed_type'] in {2, 3}:

      if self.params['repeater'] > 0:
        while not (self.params['repeater'] in repeaterConsumer.register):
          self.logger.info('Waiting for repeater '
            + str(self.params['repeater']) + ' to register...')
          sleep(10)
        self.repeater = (
          repeaterConsumer.register[self.params['repeater']]['myself'])
        while not (self.repeater.host_register_complete):
          self.logger.info('Waiting for repeater '
            + str(self.params['repeater']) + ' to collect host list...')
          sleep(10)
        self.repeater_running = True
        try:
          probe = loads(self.repeater.probe(self.params['url_vid']))
          self.online = True
        except json.decoder.JSONDecodeError:
          self.online = False
      else:
        self.online = True
        try:
          if self.params['feed_type'] == 2:
            probe = ffmpeg.probe(self.params['url_vid'])
          elif self.params['feed_type'] == 3:
            probe = ffmpeg.probe(self.params['url_vid'], rtsp_transport='tcp')
        except ffmpeg._run.Error:
          if self.logger is not None:
            mylogger.warning(
              'ffprobe did not work (camera #'+str(self.id)+' offline?)')
          self.online = False
      if self.online:
        i = 0
        while probe['streams'][i]['codec_type'] != 'video':
          i += 1
        #print(probe['streams'][i])
        self.setparams({
          'xres' : probe['streams'][i]['width'],
          'yres' : probe['streams'][i]['height'],
        }, writedb=True)

  def run(self, logger=None):
    self.old_frames = 0
    self.old_out_time_us = 0
    self.old_dup_frames = 0
    self.old_drop_frames = 0
    self.thistime = time()
    self.logger = logger
    self.wd_ts = time()
    self.imagecheck = 0
    multitimer.MultiTimer(interval=10, function=self.watchdog, 
      runonstart=False).start()
    multitimer.MultiTimer(interval=1, function=self.checkmp4, 
      runonstart=False).start()
    if self.params['feed_type'] in {2, 3}:
      multitimer.MultiTimer(interval=60, function=self.cleanup, 
        runonstart=False).start()
      self.fifo = fifoopen(self.fifoname, O_RDONLY | O_NONBLOCK)
    self.setparams({'lastused' : timezone.now(),}, writedb=True)
    if self.id > 0:
      while not self.online:
        self.set_x_y(self.logger)
        if not self.online:
          sleep(60)
    self.int_mask_list = []
    for mask_line in mask.objects.filter(cam=self.id):
      self.int_mask_list.append(loads(mask_line.definition))
    self.int_mask_list = mask_list(self.int_mask_list)
    self.refresh_mask()
    super().run(logger)

  def run_one(self, dummy):
    thistime = time()
    while True:
      if (self.view_count > 0) or (self.data_count > 0) or (self.record_count > 0):
        if self.cam_active:
          if (self.record_count == 0) and (self.ff_proc_2 is not None):
            self.ff_proc_2.stdin.close()
            self.ff_proc_2.kill()
            self.ff_proc_2 = None
            self.logger.info('Cam #'+str(self.id)+' stopped recording')
          if (self.record_count > 0) and (self.ff_proc_2 is None):
            if self.ff_proc_1 is not None:
              self.ff_proc_1.kill()
            self.newprocess() 
            self.logger.info('Cam #'+str(self.id)+' started recording')
        else:
          self.newprocess() 
          self.logger.info('Cam #'+str(self.id)+' is on')
          self.cam_active = True
        self.cam_ts = None
        break
      else:
        if self.cam_active:
          if self.cam_ts is None:
            self.cam_ts = time()
            break
          else:
            if (time() - self.cam_ts) < 60:
              break
            else:
              self.logger.info('Cam #'+str(self.id)+' is off')
              self.cam_active = False
              self.cam_ts = None
              if self.ff_proc_1 is not None:
                self.ff_proc_1.kill()
              if self.ff_proc_2 is not None:
                self.ff_proc_2.kill()
              self.ff_proc_1 = None
              self.ff_proc_2 = None
        else:
          sleep(0.01)
    while True:
      if self.params['feed_type'] == 1:
        newtime = time()
        if (newtime - self.lasttime) >= 10:
          self.setparams(
            {'fpsactual' : self.fps_counter/(newtime - self.lasttime),},
            writedb=True)
          self.fps_counter = 0
          self.lasttime = newtime
        else:
          self.fps_counter += 1
        frame = None
        oldtime = thistime
        thistime = time()
        try:
          frame = requests.get(self.params['url_img'], timeout=60).content
          frame = c_convert(frame, typein=1, typeout=3)
          if self.ff_proc_2 is not None:
            flatframe = frame.flatten()
            for i in range(round((thistime-oldtime)*self.params['fpslimit'])):
              self.ff_proc_2.stdin.write(flatframe)
        except requests.exceptions.ReadTimeout:
          self.logger.warning('Cam #' + str(self.id)
            + ' had timeout while getting JPG')
        except requests.exceptions.ConnectTimeout:
          self.logger.warning('Cam #' + str(self.id)
            + ' had timeout while connecting for JPG')
        except requests.exceptions.ConnectionError:
          self.logger.warning('Cam #' + str(self.id)
            + ' could not connect for getting JPG')
          sleep(60)
        if frame is not None:
          break
      elif self.params['feed_type'] in {2, 3}:  
        while True:
          try:
            mymessage = fiforead(self.fifo, 300).split()
            if len(mymessage) == 0:
              break
            else:
              newtime = time()
              if (newtime - self.lasttime) >= 10:
                #print(mymessage)
                try:
                  new_frames = mymessage[0].decode().split('=')
                  new_frames = int(new_frames[1])
                  frames = new_frames - self.old_frames
                  self.old_frames = new_frames
                  new_out_time_us = mymessage[5].decode().split('=')
                  new_out_time_us = int(new_out_time_us[1])
                  out_time_us = new_out_time_us - self.old_out_time_us
                  self.old_out_time_us = new_out_time_us
                  new_dup_frames = mymessage[8].decode().split('=')
                  new_dup_frames = int(new_dup_frames[1])
                  dup_frames = new_dup_frames - self.old_dup_frames
                  self.old_dup_frames = new_dup_frames
                  new_drop_frames = mymessage[9].decode().split('=')
                  new_drop_frames = int(new_drop_frames[1])
                  drop_frames = new_drop_frames - self.old_drop_frames
                  self.old_drop_frames = new_drop_frames
                  if out_time_us == 0:
                    self.setparams({'fpsactual' : 0.0,}, writedb=True)
                  else:
                    self.setparams(
                      {'fpsactual' : ((frames - dup_frames + drop_frames)
                        * 1000000 / out_time_us),}, 
                      writedb=True)
                  self.lasttime = newtime
                except ValueError:
                  self.logger.warning('Cam #' + str(self.id)
                    + ' could not interpret capture information:')
                  self.logger.warning(str(mymessage))
          except BlockingIOError:
            break
        try:
          in_bytes = self.ff_proc_1.stdout.read(self.params['xres'] 
            * self.params['yres'] * 3)
          frame = np.frombuffer(in_bytes, np.uint8).reshape(self.params['yres'],
            self.params['xres'], 3)
          if self.ff_proc_2 is not None:
            self.ff_proc_2.stdin.write(in_bytes)
          break
        except (ValueError, AttributeError):
          sleep(0.01)
    self.getting_newprozess = False
    imagesum = np.sum(frame)
    if self.imagecheck != imagesum:
      self.imagecheck = imagesum
      if self.params['apply_mask'] and (self.mask is not None):
        frame = cv.bitwise_and(frame, self.mask)
      self.wd_ts = thistime
      return((3, frame, thistime))
    else:
      return(None)
