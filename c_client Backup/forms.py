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

from django import forms
from .models import cam, detector, eventer

class CamForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['url_img'].required = False
		self.fields['url_vid'].required = False

	class Meta:
		model = cam
		fields = ('url_img', 'url_vid', 'feed_type', 'fpslimit')
		widgets = { 
			'url_img' : forms.TextInput(attrs={'size': 70}),
			'url_vid' : forms.TextInput(attrs={'size': 70}),
			'fpslimit' : forms.NumberInput(attrs={'size': 10, 'min' : 0, 'max' : 100, 'step' : 0.1}), 
		}

class DetectorForm(forms.ModelForm):

	class Meta:
		model = detector
		fields = ('backgr_delay', 'dilation', 'erosion', 'max_size', 'threshold', 'max_rect')
		widgets = {
			'backgr_delay' : forms.NumberInput(attrs={'size': 10, 'min' : 0, 'max' : 100}), 
			'dilation' : forms.NumberInput(attrs={'size': 10, 'min' : 1, 'max' : 200}), 
			'erosion' : forms.NumberInput(attrs={'size': 10, 'min' : 0, 'max' : 100}), 
			'max_size' : forms.NumberInput(attrs={'size': 10, 'min' : 1, 'max' : 200}), 
			'threshold' : forms.NumberInput(attrs={'size': 10, 'min' : 1, 'max' : 254}), 
			'max_rect' : forms.NumberInput(attrs={'size': 10, 'min' : 1, 'max' : 100}), 
		}

class EventerForm(forms.ModelForm):

	class Meta:
		model = eventer
		fields = ('margin', 'event_time_gap', 'school', 'alarm_email')
		widgets = {
			'margin' : forms.NumberInput(attrs={'size': 10, 'min' : 0, 'max' : 100}), 
			'event_time_gap' : forms.NumberInput(attrs={'size': 10, 'min' : 1, 'max' : 3600}), 
			'school' : forms.NumberInput(attrs={'size': 10, 'min' : 1, 'max' : 100}), 
			'alarm_email' : forms.TextInput(attrs={'size': 70}),
		}

class CamTestForm(forms.Form):
  url = forms.CharField(label='Url', max_length=200)
  feed_type = forms.ChoiceField(label='Feed Type', choices=[
    (2, 'Others'),
    (1, 'JPeg'),
    (3, 'RTSP'),
])
