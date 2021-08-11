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

import numpy as np
from threading import Lock
import cv2 as cv
from datetime import datetime
from random import randint
from os import path, makedirs
from concurrent import futures
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib, ssl
from django.db import connection
from django.utils import timezone
from django.db.utils import OperationalError
from .models import event, event_frame, school
from .l_tools import ts2filename, uniquename, randomfilter, np_mov_avg
from .c_tools import djconf, classes_list
from .c_tfworker import tfworker

e = futures.ThreadPoolExecutor(max_workers=1000)

class c_event(list):

  def __init__(self):
    super().__init__()
    self.frames_lock = Lock()
    self.pred_max = None
    self.pred_ave = None
    self.xdim = djconf.getconfigint('xdim', 331)
    self.ydim = djconf.getconfigint('ydim', 331)
    self.frames = []
    self.maxblock = djconf.getconfigint('tfw_maxblock', 8)
    self.number_of_frames = djconf.getconfigint('frames_event', 32)
    self.thread = None
    self.isrecording = False
    self.goes_to_school = False
    self.status = 0
    self.pred_busy = False

  def put_first_frame(self, frame, margin, xmax, ymax, classes_list):
    self.tf_w_index = tfworker.register()
    self.classes_list = classes_list
    self.start = frame[2]
    self.end = frame[2]
    self.append(max(0, frame[3] - margin))
    self.append(min(xmax, frame[4] + margin))
    self.append(max(0, frame[5] - margin))
    self.append(min(ymax, frame[6] + margin))
    self.append(False)
    self.next_to_send = 0
    self.predictions = np.zeros((0,len(classes_list)))
    self.frames.append(frame)
    eventline = event()
    while True:
      try:
        eventline.save()
        break
      except OperationalError:
        connection.close()
    self.id =  event.objects.latest('id').id

  def shrink(self):
    if len(self.frames) > self.next_to_send:
      firstpart = self.frames[:self.next_to_send]
      secondpart = self.frames[self.next_to_send:]
      self.frames = firstpart + randomfilter(secondpart, self.maxblock)

  def pred_read(self, radius=3, max=0.0, ave=0.0, last=0.0):
    result2 = np.zeros((len(classes_list)), np.float32)
    if self.predictions.shape[0] <= 0:
      return(result2)
    else:
      if radius == 0:
        result1 = self.predictions[:]
      else:
        result1 = np_mov_avg(self.predictions, radius)
      if max != 0:
        result2 += np.max(result1, axis=0) * max
      if ave != 0:
        result2 += np.average(result1, axis=0) * ave
      if last != 0:
        result2 += result1[-1] * last
      return(np.clip(result2, 0.0, 1.0))

  def pred_thread(self, logger= None):
    while len(self.frames) > self.predictions.shape[0]:
      newpredictions = tfworker.users[self.tf_w_index].fifoout.get(block=True)
      self.predictions = np.vstack((self.predictions, newpredictions))
  

  def get_predictions(self, myschool, logger=None):
    if not self.pred_busy:
      self.pred_busy = True
      if len(self.frames) > self.next_to_send:
        pred_length = len(self.frames)
        imglist = np.empty((0, self.xdim, self.ydim, 3), np.uint8)
        for i in range(self.next_to_send, pred_length):
          np_image = cv.resize(self.frames[i][1],(self.xdim, self.ydim))
          np_image = np.expand_dims(np_image, axis=0)
          imglist = np.append(imglist, np_image, 0)
        self.next_to_send = pred_length
        if self.tf_w_index is not None:
          tfworker.users[self.tf_w_index].fifoin.put([myschool, imglist])
          if (self.thread is None) or (self.thread.done()):
            self.thread = e.submit(self.pred_thread, logger)
      self.pred_busy = False
  
  def wait_for_pred_done(self):
    while len(self.frames) > self.predictions.shape[0]:
      sleep(0.01)

  def pred_is_done(self, limit = None):
    if limit is None:
      return(len(self.frames) == self.predictions.shape[0])
    else:
      return(limit <= self.predictions.shape[0])

  def p_string(self):
    predline = '['
    for i in range(len(self.classes_list)):
      if (self.pred_read(max=1.0)[i] >= 0.5):
        if (predline != '[') :
          predline += ','
        predline += self.classes_list[i]
    return(predline+']')

  def frames_filter(self, outlength):
    with self.frames_lock:
      result = self.frames[:self.predictions.shape[0]]
    if len(result) > outlength:
      predlist = self.predictions.tolist()
      sortindex = list(range(len(result)))
      sortindex.sort(key=lambda item: max(predlist[item][1:]), reverse=True)
      sortindex = sortindex[:outlength]
      sortindex.sort()
      result = [result[i] for i in sortindex]
    return(result)

  def save(self, myschool, eventer_id, eventer_name, goes_to_school=True, 
      to_email='', video_name=''):
    frames_to_save = self.frames_filter(self.number_of_frames)
    eventlines = event.objects.filter(id=self.id)
    if len(eventlines) > 0:
      eventline = eventlines[0]
      eventline.p_string=eventer_name+'('+str(eventer_id)+'): '+self.p_string()
      eventline.start=timezone.make_aware(datetime.fromtimestamp(self.start))
      eventline.end=timezone.make_aware(datetime.fromtimestamp(self.end))
      eventline.xmin=self[0]
      eventline.xmax=self[1]
      eventline.ymin=self[2]
      eventline.ymax=self[3]
      eventline.numframes=len(frames_to_save)
      eventline.school= school.objects.get(id=myschool)
      eventline.done = not goes_to_school
      eventline.save()
      self.mailimages = []
      for item in frames_to_save:
        pathname = djconf.getconfig('schoolframespath')
        pathadd = str(myschool)+'/'+str(randint(0,99))
        if not path.exists(pathname+'/'+pathadd):
          makedirs(pathname+'/'+pathadd)
        filename = uniquename(pathname, pathadd+'/'+ts2filename(item[2], 
          noblank=True), 'bmp')
        self.mailimages.append(filename.replace('/', '$', 2))
        cv.imwrite(pathname+filename, item[1])
        frameline = event_frame(
          time=timezone.make_aware(datetime.fromtimestamp(item[2])),
          name=filename,
          x1=item[3],
          x2=item[4],
          y1=item[5],
          y2=item[6],
          event=eventline,
        )
        frameline.save()
      if len(to_email) > 0:
        self.send_emails(to_email, video_name, eventer_id, eventer_name)

  def send_emails(self, to_email, video_name, eventer_id, eventer_name):
    to_email = to_email.split()
    for receiver in to_email:
      mylist = self.pred_read(max=1.0)[1:].tolist()
      maxpos = mylist.index(max(mylist))  
      message = MIMEMultipart('alternative')
      message['Subject'] = ('#'+str(eventer_id) + '(' + eventer_name + '): '
        + self.classes_list[maxpos+1])
      message['From'] = (djconf.getconfig('smtp_name', 'CAM-AI Emailer') 
        +' <'+djconf.getconfig('smtp_email')+'>')
      message['To'] = receiver

      text = ('Hello CAM-AI user,\n' 
        + 'We had some movement.\n'  
        + 'Here are the images: \n')  
      for item in self.mailimages:
        text += djconf.getconfig('client_url')+'getbmp/0/'+item+' <br> \n' 
      text += ('...and here is the movie: \n' 
        + djconf.getconfig('recordingsurl')+video_name+' <br> \n') 
      html = ('<html><body><p>Hello CAM-AI user, <br>\n' 
        + 'We had some movement. <br> \n' 
        + 'Here are the images: <br> \n')
      for item in self.mailimages:
        html += ('<img src="' + djconf.getconfig('client_url') + 'getbmp/0/' 
          +item+'">\n') 
      html += ('<br>...and here is the movie: <br> \n' 
        + djconf.getconfig('recordingsurl')+video_name+' <br>\n')

      message.attach(MIMEText(text, 'plain'))
      message.attach(MIMEText(html, 'html'))
      context = ssl.create_default_context()
      with smtplib.SMTP_SSL(djconf.getconfig('smtp_server'), 
          djconf.getconfigint('smtp_port', 465), 
          context=context) as server:
        server.login(djconf.getconfig('smtp_account'), 
          djconf.getconfig('smtp_password'))
        server.sendmail(djconf.getconfig('smtp_email'), 
          receiver, message.as_string())

  def unregister(self):
    tfworker.unregister(self.tf_w_index)
    self.tf_w_index = None

