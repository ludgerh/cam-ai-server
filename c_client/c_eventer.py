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

from time import time, sleep
from shutil import copyfile
from os import remove
from subprocess import run
from threading import Thread
from collections import deque
import cv2 as cv
import ffmpeg
import multitimer
from traceback import format_exc
from django.forms.models import model_to_dict
from django.db.utils import OperationalError
from django.db import connection
from .models import eventer, evt_condition, event
from .c_tools import hasoverlap, rect_btoa, djconf
from .c_buffer import c_buffer
from .c_tfconfig import tf_workers
from .c_device import c_device
from .c_event import c_event
from .c_alarm import alarm
from .c_schools import get_taglist

class c_eventer(c_device):

  def __init__(self, id=None):
    self.modelclass = eventer
    self.frameslist_present = False
    super().__init__(id, type='E')
    self.tf_worker = tf_workers[0]
    self.eventdict = {}
    self.tf_w_index = self.tf_worker.register(self.eventdict)
    self.tf_worker.run_out(0, self.tf_w_index)
    self.detectbuffer = c_buffer(getall=True)
    self.nr_of_cond_ed = 0
    self.last_cond_ed = 0
    self.inserter_ts = 0
    self.cam_count_old = False
    self.vid_count_old = False
    self.classes_list=[item.name for item in get_taglist(self.params['school'])]
    self.cachedict = {}
    self.frameslist = deque()
    self.frameslist_present = True
    self.display_busy = False
    self.check_busy = False
    self.display_ts = 0
    self.buffer_ts = time()

  def run(self, logger):
    self.logger = logger
    self.vid_str_dict = {}
    multitimer.MultiTimer(interval=0.5, function=self.check_events, 
      runonstart=False).start()
    multitimer.MultiTimer(interval=0.1, function=self.display_events, 
      runonstart=False).start()
    super().run(self.logger)

  def merge_events(self):
    while True:
      changed = False
      for i in self.eventdict.copy():
        if (i in self.eventdict) and (self.eventdict[i].status == 0):
          for j in self.eventdict.copy():
            if ((j > i) and (j in self.eventdict) 
                and (self.eventdict[j].status == 0) 
                and hasoverlap(self.eventdict[i], self.eventdict[j])):
              self.eventdict[i][0] = min(self.eventdict[i][0], 
                self.eventdict[j][0])
              self.eventdict[i][1] = max(self.eventdict[i][1], 
                self.eventdict[j][1])
              self.eventdict[i][2] = min(self.eventdict[i][2], 
                self.eventdict[j][2])
              self.eventdict[i][3] = max(self.eventdict[i][3], 
                self.eventdict[j][3])
              self.eventdict[i].end = max(self.eventdict[i].end, 
                self.eventdict[j].end)
              self.eventdict[j].status = -3
              self.eventdict[i].merge_frames(self.eventdict[j])
              self.eventdict[j].isrecording = False
              self.eventdict[j].goes_to_school = False
              changed = True
      if not changed:
        break

  def add_view_count(self):
    super().add_view_count()
    self.mydetector.add_data_count()

  def take_view_count(self):
    super().take_view_count()
    self.mydetector.take_data_count()
    if self.view_count == 0:
      self.frameslist.clear()

  def postinit(self):
    super().postinit()
    self.cond_dict = {1:[], 2:[], 3:[], 4:[], 5:[]}
    condition_lines = evt_condition.objects.filter(eventer_id=self.id)
    for item in condition_lines:
      self.cond_dict[item.reaction].append(model_to_dict(item))
    self.set_cam_counts()

  def build_strings(self, reaction):
    return([self.build_string(item) for item in self.cond_dict[reaction]])

  def build_string(self, i):
    if i['c_type'] == 1:
	    result = 'Any movement detected'
    elif  i['c_type'] in {2, 3}:
	    result = str(i['x'])+' predictions are '
    elif i['c_type']  in {4, 5}:
	    result = 'Tag "'+self.classes_list[i['x']]+'" is '
    elif i['c_type'] == 6:
	    result = ('Tag "'+self.classes_list[i['x']]+'" is in top '
        +str(round(i['y'])))
    if i['c_type'] in {2,4}:
	    result += 'above or equal '+str(i['y'])
    elif i['c_type'] in {3,5}:
	    result += 'below or equal '+str(i['y'])
    return(result)

  def inserter(self, logger): 
    while True:
      while (not self.tf_worker.check_ready(self.tf_w_index)):
        sleep(djconf.getconfigfloat('long_brake', 1.0))
      while True:
        if ((self.view_count == 0) and (self.data_count == 0) 
            and (self.record_count == 0)):
          sleep(djconf.getconfigfloat('short_brake', 0.01))
        else:
          break
      margin = self.params['margin']
      frame = self.detectbuffer.getframe()
      found = None

      for idict in self.eventdict.copy():
        if ((self.eventdict[idict].end > (frame[2] - 
            self.params['event_time_gap']))
          and hasoverlap((frame[3]-margin, frame[4]+margin, 
            frame[5]-margin, frame[6]+margin), self.eventdict[idict])
          and (self.eventdict[idict].status == 0)):
          found = self.eventdict[idict]
          break
      if found is None:
        myevent = c_event(self.tf_worker, self.tf_w_index, frame, 
          self.params['margin'], self.params['xres']-1, self.params['yres']-1, 
          self.classes_list, self.params['school'], logger)
        self.eventdict[myevent.id] = myevent
      else: 
        s_factor = 0.1 # user changeable later: 0.0 -> No Shrinking 1.0 50%
        if (frame[3] - margin) <= found[0]:
          found[0] = max(0, frame[3] - margin)
        else:
          found[0] = round(((frame[3] - margin) * s_factor + found[0]) 
            / (s_factor+1.0))
        if (frame[4] + margin) >= found[1]:
          found[1] = min(self.params['xres']-1, frame[4] + margin)
        else:
          found[1] = round(((frame[4] + margin) * s_factor + found[1]) 
            / (s_factor+1.0))
        if (frame[5] - margin) <= found[2]:
          found[2] = max(0, frame[5] - margin)
        else:
          found[2] = round(((frame[5] - margin) * s_factor + found[2]) 
            / (s_factor+1.0))
        if (frame[6] + margin) >= found[3]:
          found[3] = min(self.params['yres']-1, frame[6] + margin)
        else:
          found[3] = round(((frame[6] + margin) * s_factor + found[3]) 
            / (s_factor+1.0))
        found.end = frame[2]
        found.add_frame(frame)
      self.merge_events()
      self.inserter_ts = frame[2]

  def check_events(self):
    try:
      if self.check_busy:
        return()
      self.check_busy = True
      for idict in self.eventdict.copy():
        if self.eventdict[idict].status <= -2:
          if self.eventdict[idict].nrofcopies == 0: 
            if not (self.eventdict[idict].isrecording 
                or self.eventdict[idict].goes_to_school): 
              while True:
                try:
                  event.objects.filter(id=self.eventdict[idict].id).delete()
                  break
                except OperationalError:
                  connection.close()
            del self.eventdict[idict]
        else:
          if (((self.eventdict[idict].end < (time() 
                - self.params['event_time_gap'])) 
              or (self.eventdict[idict].end > (self.eventdict[idict].start 
                + 300.0))) 
              and (not self.eventdict[idict].ts)):
            self.eventdict[idict].ts = self.eventdict[idict].end
          if (self.eventdict[idict].ts and 
            self.eventdict[idict].pred_is_done(ts = self.eventdict[idict].ts)):
            predictions = self.eventdict[idict].pred_read(radius=10, max=1.0)
            self.eventdict[idict].goes_to_school = self.resolve_rules(2, 
              predictions)
            self.eventdict[idict].isrecording = (
              self.eventdict[idict].isrecording or self.resolve_rules(3,
                predictions))
            if self.resolve_rules(4, predictions):
              self.eventdict[idict].to_email = self.params['alarm_email']
            else:
              self.eventdict[idict].to_email = ''
            if self.resolve_rules(5, predictions):
              alarm(self.id, self.params['name'], predictions, 
                self.params['school'], self.logger)
            if (self.eventdict[idict].goes_to_school 
                or self.eventdict[idict].isrecording):
              if self.eventdict[idict].isrecording:
                if ((self.parent.latest_ready_video() is not None) 
                    and (self.eventdict[idict].end 
                      <= self.parent.latest_ready_video()[0])):
                  my_vid_list = []
                  my_vid_str = ''
                  with self.parent.vid_list_lock:
                    for i in range(len(self.parent.vid_list)):
                      if (self.eventdict[idict].start 
                          <= self.parent.vid_list[i][0]):
                        my_vid_list.append(self.parent.vid_list[i][1])
                        my_vid_str += self.parent.vid_list[i][2]
                        if (self.parent.vid_list[i][0] 
                            > self.eventdict[idict].end):
                          if (len(self.parent.vid_list) >= (i + 2)):
                            my_vid_list.append(self.parent.vid_list[i+1][1])
                            my_vid_str += self.parent.vid_list[i+1][2]
                          break
                  if my_vid_str in self.vid_str_dict:
                    self.eventdict[idict].savename=self.vid_str_dict[my_vid_str]
                    isdouble = True
                  else:
                    self.eventdict[idict].savename = ('E_'
                      +str(self.eventdict[idict].id).zfill(12)+'.mp4')
                    savepath = (djconf.getconfig('recordingspath')
                      +self.eventdict[idict].savename)
                    if len(my_vid_list) == 1: #presently not used
                      copyfile(djconf.getconfig('recordingspath')
                        +my_vid_list[0], savepath)
                    else:
                      tempfilename = (djconf.getconfig('recordingspath') + 'T_'
                        + str(self.eventdict[idict].id).zfill(12)+'.temp')
                      with open(tempfilename, 'a') as f1:
                        for line in my_vid_list:
                          f1.write('file '+djconf.getconfig('recordingspath') 
                            + line + '\n')
                      run(['ffmpeg', '-f', 'concat', '-safe', '0', '-v', 
                        'fatal', '-i', tempfilename, '-codec', 'copy', 
                        savepath])
                      remove(tempfilename)
                    (ffmpeg
                    .input(savepath, v='warning')
                    .output(savepath[:-3]+'webm')
                    .run_async())
                    self.vid_str_dict[my_vid_str] = self.eventdict[idict].savename
                    isdouble = False
                  eventlines = event.objects.filter(id=self.eventdict[idict].id)
                  if len(eventlines) > 0:
                    eventline = eventlines[0]
                    eventline.videoclip = self.eventdict[idict].savename[:-4]
                    eventline.double = isdouble
                    eventline.save()
                  if not isdouble:
                    run(['ffmpeg', '-ss', '00:15', '-v', 'fatal', '-i', savepath, 
                      '-vframes', '1', '-q:v', '2', savepath[:-4]+'.jpg'])
                  self.eventdict[idict].status = min(-2, 
                    self.eventdict[idict].status)
                else:  
                  self.eventdict[idict].status = -1
              else:
                self.eventdict[idict].status  = min(-2, 
                  self.eventdict[idict].status)
            else:
              self.eventdict[idict].status  = min(-2, 
                self.eventdict[idict].status)
          if ((self.eventdict[idict].status == -2)
              and (self.eventdict[idict].goes_to_school 
              or self.eventdict[idict].isrecording)):
            self.eventdict[idict].save(self.params['school'], 
              self.id, self.params['name'], 
              self.eventdict[idict].goes_to_school, 
              self.eventdict[idict].to_email, self.eventdict[idict].savename) 
      self.check_busy = False  
    except:
      self.logger.error(format_exc())
      self.logger.handlers.clear()

  def display_events(self):
    try:
      if self.display_busy:
        return()
      self.display_busy = True
      if self.view_count == 0:
        self.frameslist.clear()
        for i in self.eventdict:
          self.eventdict[i].nrofcopies = 0
          self.frameslist.clear()
        self.display_busy = False
        return()
      while len(self.frameslist) > 0:
        myframeplusevents = self.frameslist.popleft()
        all_done = True
        for item in myframeplusevents['events']:
          if ((item[0] in self.eventdict) 
              and (self.eventdict[item[0]].status >= -2)):
            myevent = self.eventdict[item[0]]
            if (not myevent.pred_is_done(ts=item[1])):
              all_done = False
              break
        if all_done:
          frame = myframeplusevents['frame']
          newimage = frame[1].copy()
          buffer_diff = min(1.0, frame[2] - self.buffer_ts)
          while (time() - self.display_ts) < (buffer_diff * 0.9):
            sleep(djconf.getconfigfloat('short_brake', 0.01))
          self.buffer_ts = frame[2]
          self.display_ts = time()
          for i in myframeplusevents['events']:
            if i[0] in self.eventdict:
              item = self.eventdict[i[0]]
              if self.eventdict[i[0]].status >= -2:
                itemold = i[2]
                predictions = item.pred_read(max=1.0)
                if djconf.getconfigbool('all_predictions', False) or (self.nr_of_cond_ed > 0):
                  if self.nr_of_cond_ed <= 0:
                    self.last_cond_ed = 1
                  if self.resolve_rules(self.last_cond_ed, predictions):
                    colorcode= (0, 255, 0)
                  else:
                    colorcode= (0, 0, 255)
                  displaylist = [(j, predictions[j]) for j in range(10)]
                  displaylist.sort(key=lambda x: -x[1])
                  cv.rectangle(newimage, rect_btoa(itemold), colorcode, 5)
                  if itemold[2] < (self.params['yres'] - itemold[3]):
                    y0 = itemold[3]+20
                  else:
                    y0 = itemold[2]-190
                  for j in range(10):
                    cv.putText(newimage, 
                      self.classes_list[displaylist[j][0]][:3]
                      +' - '+str(round(displaylist[j][1],2)), 
                      (itemold[0]+2, y0 + j * 20), 
                      cv.FONT_HERSHEY_SIMPLEX, 0.5, colorcode, 2, cv.LINE_AA)
                else:
                  imax = -1
                  pmax = -1
                  for j in range(1,len(predictions)):
                    if predictions[j] >= 0.0:
                      if predictions[j] > pmax:
                        pmax = predictions[j]
                        imax = j
                  if self.resolve_rules(1, predictions):
                    cv.rectangle(newimage, rect_btoa(itemold), (255, 0, 0), 5)
                    cv.putText(newimage, self.classes_list[imax][:3], 
                      (itemold[0]+10, itemold[2]+30), 
                      cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv.LINE_AA)
                item.nrofcopies -= 1
          self.put_one((3, newimage, frame[2]))
        else:
          self.frameslist.appendleft(myframeplusevents)
          sleep(djconf.getconfigfloat('long_brake', 1.0))
          break
      self.display_busy = False
    except:
      self.logger.error(format_exc())
      self.logger.handlers.clear()

  def run_one(self, frame):
    if self.view_count > 0:
      if len(self.frameslist) < 100:
        while (self.inserter_ts <= frame[2]) and self.eventdict:
          sleep(djconf.getconfigfloat('short_brake', 0.01))
        frameplusevents = {}
        frameplusevents['frame'] = frame
        frameplusevents['events'] = []
        for idict in self.eventdict.copy():
          if ((idict in self.eventdict) and (self.eventdict[idict].status == 0)):
            frameplusevents['events'].append((idict, self.eventdict[idict].end, self.eventdict[idict][:4]))
            self.eventdict[idict].nrofcopies += 1
        self.frameslist.append(frameplusevents)

  def resolve_rules(self, reaction, predictions):
    if predictions is None:
      return(False)
    else:
      total_and = None
      total_or = None
      for item in self.cond_dict[reaction]:
        if (total_and is not None) and (not total_and) and total_or:
          break
        else:
          if item['c_type'] == 1:
            item_result = True
          elif item['c_type'] == 2:
            count = 0
            item_result = False
            for prediction in predictions:
              if prediction >= item['y']:
                count += 1
                if count >= item['x']:
                  item_result = True
                  break
          elif item['c_type'] == 3:
            count = 0
            item_result = False
            for prediction in predictions:
              if prediction <= item['y']:
                count += 1
                if count >= item['x']:
                  item_result = True
                  break
          elif item['c_type'] == 4:
            item_result = (predictions[item['x']] >= item['y'])
          elif item['c_type'] == 5:
            item_result = (predictions[item['x']] <= item['y'])
          elif item['c_type'] == 6:
            myprediction = predictions[item['x']]
            count = 0
            item_result = True
            for prediction in predictions:
              if prediction > myprediction:
                count += 1
                if count >= item['y']:
                  item_result = False
                  break
          if item['and_or'] == 0:
            if total_and is None:
              total_and = item_result
            else:
              total_and = (total_and and item_result)
          else:
            if total_or is None:
              total_or = item_result
            else:
              total_or = (total_or or item_result)
      if total_and is None:
        if total_or is None:
          return(False)
        else:
          return(total_or)
      else:
        if total_or is None:
          return(total_and)
        else:  
          return(total_and and total_or)

  def set_cam_counts(self):
    if ((len(self.cond_dict[2]) > 0)
        or (len(self.cond_dict[3]) > 0)
        or (len(self.cond_dict[4]) > 0)
        or (len(self.cond_dict[5]) > 0)):
      if not self.cam_count_old:
        self.add_data_count()
        self.mydetector.add_data_count()
        self.cam_count_old = True
    else:
      if self.cam_count_old:
        self.take_data_count()
        self.mydetector.take_data_count()
        self.cam_count_old = False
    if len(self.cond_dict[3]) > 0:
      if not self.vid_count_old:
        self.add_record_count()
        self.vid_count_old = True
    else:
      if self.vid_count_old:
        self.take_record_count()
        self.vid_count_old = False
