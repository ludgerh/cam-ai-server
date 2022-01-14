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

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime

class stream(models.Model):
  name = models.CharField(max_length=100, default='')
  made = models.DateTimeField(default=timezone.now)
  lastused = models.DateTimeField(default=timezone.now)
  cam_xres = models.IntegerField(default=0)
  cam_yres = models.IntegerField(default=0)
  cam_fpslimit = models.FloatField("FPS limit", default=0)
  cam_fpsactual = models.FloatField(default=0)
  cam_active = models.BooleanField(default=True)
  cam_feed_type = models.IntegerField("feed type", choices=((1, 'JPeg'), (2, 'Others'), (3, 'RTSP')), default=1)
  cam_url = models.CharField("url", max_length=256, default='')
  cam_apply_mask = models.BooleanField(default=False)
  cam_repeater = models.IntegerField(default=0)
  det_fpsactual = models.FloatField(default=0)
  det_active = models.BooleanField(default=True)
  det_backgr_delay = models.IntegerField("background delay", default=3)
  det_dilation = models.IntegerField("dilation", default=50)
  det_erosion = models.IntegerField("erosion", default=2)
  det_max_size = models.IntegerField("max. size", default=100)
  det_threshold = models.IntegerField("threshold", default=70)
  det_max_rect = models.IntegerField("max. number", default=10)
  evt_fpsactual = models.FloatField(default=0)
  evt_active = models.BooleanField(default=True)
  evt_school = models.IntegerField("school", default=1)
  evt_margin = models.IntegerField("frame margin", default=50)
  evt_event_time_gap = models.IntegerField("new event gap", default=60)
  evt_alarm_email = models.CharField("alarm email", max_length=255, default='')

  def __str__(self):
    return('Stream model, name: '+self.name)

class tag(models.Model):
  name =  models.CharField(max_length=100)
  description = models.CharField(max_length=100)
  school = models.SmallIntegerField(default=0)
  replaces = models.SmallIntegerField(default=-1)

  def __str__(self):
    return(self.name)

class school(models.Model):
  name =  models.CharField(max_length=100)
  size = models.IntegerField(default=0)
  dir = models.CharField(max_length=256)
  trigger = models.IntegerField(default=500)
  lastfile = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
  active = models.IntegerField(default=1)
  last_id_mf = models.IntegerField(default=0)
  last_id_of = models.IntegerField(default=0)
  train_on_all = models.BooleanField(default=False)
  do_filter = models.BooleanField(default=False)
  used_by_others = models.BooleanField(default=False)
  load_model_nr = models.SmallIntegerField(default=1)
  l_rate_min = models.CharField(max_length=20, default = '-1')
  l_rate_max = models.CharField(max_length=20, default = '-1')
  e_school = models.IntegerField(default=1)
  model_type = models.CharField(max_length=50, default = 'cam-ai_model')

  def __str__(self):
    return(self.name)

class trainframe(models.Model):
  made = models.DateTimeField()
  school = models.SmallIntegerField()
  name =  models.CharField(max_length=256)
  code =  models.CharField(max_length=2)
  c0 = models.SmallIntegerField()
  c1 = models.SmallIntegerField()
  c2 = models.SmallIntegerField()
  c3 = models.SmallIntegerField()
  c4 = models.SmallIntegerField()
  c5 = models.SmallIntegerField()
  c6 = models.SmallIntegerField()
  c7 = models.SmallIntegerField()
  c8 = models.SmallIntegerField()
  c9 = models.SmallIntegerField()
  checked = models.SmallIntegerField()
  made_by = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.SET_NULL, null=True)

  def __str__(self):
    return(self.name)

class setting(models.Model):
	setting =  models.CharField(max_length=100)
	index = models.SmallIntegerField()
	value =  models.CharField(max_length=100)
	comment =  models.CharField(max_length=256)

	def __str__(self):
		return(self.setting)

class fit(models.Model):
	made = models.DateTimeField()
	minutes = models.FloatField()
	school = models.IntegerField()
	epochs = models.IntegerField()
	nr_tr = models.IntegerField()
	nr_va = models.IntegerField()
	loss = models.FloatField()
	cmetrics = models.FloatField()
	hit100 = models.FloatField(default=0)
	val_loss = models.FloatField()
	val_cmetrics = models.FloatField()
	val_hit100 = models.FloatField(default=0)
	cputemp = models.FloatField()
	cpufan1 = models.FloatField()
	cpufan2 = models.FloatField()
	gputemp = models.FloatField()
	gpufan = models.FloatField()
	description = models.TextField()

	def __str__(self):
		return('Fit made ' + str(self.made))

class epoch(models.Model):
	fit = models.ForeignKey(fit, on_delete=models.CASCADE)
	loss = models.FloatField()
	cmetrics = models.FloatField()
	hit100 = models.FloatField(default=0)
	val_loss = models.FloatField()
	val_cmetrics = models.FloatField()
	val_hit100 = models.FloatField(default=0)

	def __str__(self):
		return('epoch model (TBD ...)')

class userinfo(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	school = models.ForeignKey(school, on_delete=models.SET_NULL, null=True)
	counter = models.IntegerField(default=0)

	def __str__(self):
		return('userinfo model (TBD ...)')

class event(models.Model):
  p_string = models.CharField(max_length=255, default='[]')
  start = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
  end = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
  xmin = models.IntegerField(default=0)
  xmax = models.IntegerField(default=0)
  ymin = models.IntegerField(default=0)
  ymax = models.IntegerField(default=0)
  numframes = models.IntegerField(default=0)
  school = models.ForeignKey(school, on_delete=models.CASCADE, default=1)
  userlock = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.SET_NULL, null=True)
  locktime = models.DateTimeField(default=None, null=True)
  done = models.BooleanField(default=False)
  videoclip = models.CharField(max_length=256, default='')
  double = models.BooleanField(default=False)

  def __str__(self):
    return('event model (TBD ...)')
	
class event_frame(models.Model):
	time = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
	status = models.SmallIntegerField(default=0)
	name = models.CharField(max_length=100)
	x1 = models.IntegerField(default=0)
	x2 = models.IntegerField(default=0)
	y1 = models.IntegerField(default=0)
	y2 = models.IntegerField(default=0)
	event = models.ForeignKey(event, on_delete=models.CASCADE, default=1)
	trainframe = models.BigIntegerField(default=0)

	def __str__(self):
		return('event_frames model (TBD ...)')

class cam(models.Model):
# from c_device.py
	name = models.CharField(max_length=100, default='')
	made = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
	lastused = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
	xres = models.IntegerField(default=0)
	yres = models.IntegerField(default=0)
	fpslimit = models.FloatField("FPS limit", default=0)
	fpsactual = models.FloatField(default=0)
	active = models.BooleanField(default=True)
	outbuffers = models.CharField(max_length=255, default='[]')
# from c_cam.py
	feed_type = models.IntegerField("feed type", choices=((1, 'JPeg'), (2, 'Others'), (3, 'RTSP')), default=1)
	url_img = models.CharField("image url", max_length=256, default='')
	url_vid = models.CharField("video url", max_length=256, default='')
	apply_mask = models.BooleanField(default=False)
	repeater = models.IntegerField(default=0)

	def __str__(self):
		return('cams model (TBD ...)')

class view(models.Model):
# from c_device.py
	name = models.CharField(max_length=100, default='')
	made = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
	lastused = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
	xres = models.IntegerField(default=0)
	yres = models.IntegerField(default=0)
	fpslimit = models.FloatField(default=0)
	fpsactual = models.FloatField(default=0)
	active = models.BooleanField(default=True)
	outbuffers = models.CharField(max_length=255, default='[]')
# from c_view.py
	source_type = models.CharField(max_length=1, default='X')
	source_id = models.IntegerField(default=0)

	def __str__(self):
		return(self.source_type+str(self.source_id)+'-'+self.name+'>')

class detector(models.Model):
# from c_device.py
	name = models.CharField(max_length=100, default='')
	made = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
	lastused = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
	xres = models.IntegerField(default=0)
	yres = models.IntegerField(default=0)
	fpslimit = models.FloatField(default=0)
	fpsactual = models.FloatField(default=0)
	active = models.BooleanField(default=True)
	outbuffers = models.CharField(max_length=255, default='[]')
# from c_detector.py
	backgr_delay = models.IntegerField("background delay", default=3)
	dilation = models.IntegerField("dilation", default=50)
	erosion = models.IntegerField("erosion", default=2)
	max_size = models.IntegerField("max. size", default=100)
	threshold = models.IntegerField("threshold", default=70)
	max_rect = models.IntegerField("max. number", default=10)
	eventer = models.IntegerField(default=1)

	def __str__(self):
		return('detectors model (TBD ...)')

class eventer(models.Model):
# from c_device.py
  name = models.CharField(max_length=100, default='')
  made = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
  lastused = models.DateTimeField(default=timezone.make_aware(datetime(1900, 1, 1)))
  xres = models.IntegerField(default=0)
  yres = models.IntegerField(default=0)
  fpslimit = models.FloatField(default=0)
  fpsactual = models.FloatField(default=0)
  active = models.BooleanField(default=True)
  outbuffers = models.CharField(max_length=255, default='[]')
# from c_eventer.py
  school = models.IntegerField("school", default=1)
  margin = models.IntegerField("frame margin", default=50)
  event_time_gap = models.IntegerField("new event gap", default=60)
  alarm_email = models.CharField("alarm email", max_length=255, default='')

  def __str__(self):
    return(str(self.id)+' - '+self.name+' - '+str(self.school))

class mask(models.Model):
	cam = models.ForeignKey(cam, on_delete=models.CASCADE, null=True)
	name = models.CharField(max_length=100, default='')
	definition = models.CharField(max_length=500, default='[]')

	def __str__(self):
		return('masks model (TBD ...)')

class evt_condition(models.Model):
	eventer = models.ForeignKey(eventer, on_delete=models.CASCADE)
	reaction = models.IntegerField("reaction", choices=(
		(1, 'show frame'),
		(2, 'send school'),
		(3, 'record video'),
		(4, 'send email'),
		(5, 'alarm'),
	), default=0)
	and_or = models.IntegerField("and_or", choices=((0, 'and'), (1, 'or')), default=0)
	c_type = models.IntegerField("c_type", choices=(
		(1, 'any movement detection'),
		(2, 'x values above or equal y'),
		(3, 'x values below or equal y'),
		(4, 'tag x is above or equal y'),
		(5, 'tag x is below or equal y'),
		(6, 'tag x is in top y'),
	), default=1)
	x = models.IntegerField("x", default=1)
	y = models.FloatField("y", default=0.5)

	def __str__(self):
		return('evt_conditions model (TBD ...)')

class access_control(models.Model):
  vtype = models.CharField(max_length=1) # 'C', 'D', 'E', 'S' or '0'
  vid = models.IntegerField()
  u_g = models.CharField(max_length=1, default='U') # 'U' = user, 'G' = group
  u_g_nr = models.IntegerField(default=0) # 0 = all users/groups
  r_w  = models.CharField(max_length=1, default='R') # 'R' = read, 'W' = write, '0' = read and write

  def __str__(self):
    return(self.vtype+'_'+str(self.vid)+' '+self.u_g+'_'+str(self.u_g_nr)+' '+self.r_w)

class repeater(models.Model):
  password = models.CharField(max_length=128)
  active = models.BooleanField(default=True)

  def __str__(self):
    return('repeaters model (TBD ...)')

class view_log(models.Model):
  v_type = models.CharField(max_length=1)
  v_id =  models.IntegerField()
  start = models.DateTimeField()
  stop = models.DateTimeField()
  user = models.IntegerField()
  active = models.BooleanField(default=True)

  def __str__(self):
    return('view_logs model (TBD ...)')
  
