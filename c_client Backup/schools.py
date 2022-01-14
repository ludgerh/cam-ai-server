#!/usr/bin/env python
# coding: utf-8

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



from .c_tools import djconf
from c_client.models import school, trainframe
from django.db.models import Max

catfilterdict = {}
for i in range(1,10):
	catfilterdict['c'+str(i)] = 0

class oneschool:

	def __init__(self, id, name, type, size, dir, trigger, lastclean):
		self.id = id
		self.name = name
		self.type = type # 0: Standard 1: Specific
		self.sqlname = 'trainframes_m'+str(self.id)
		self.dir = dir
		self.size = size
		self.trigger = trigger
		self.lastclean = lastclean
		self.lastline_mf = 0
		self.lastline_of = 0

	def get_newline_count(self, filter=True):
		line = trainframe.objects.filter(school=self.id, checked=1).aggregate(Max('id'))
		lastline = line['id__max']
		if (lastline is None):
			lastline = 0
		if filter:
			self.lastline_mf = lastline
			before = djconf.getconfigint('last_id_mf', 0, self.id)
		else:
			self.lastline_of = lastline
			before = djconf.getconfigint('last_id_of', 0, self.id)
		filterdict = {'school':self.id, 'checked':1, 'id__gt':before}
		if filter:
			filterdict.update(catfilterdict)
		return(trainframe.objects.filter(**filterdict).count())

	def reset_newline_count(self, filter=True):
		if filter:
			djconf.setconfigint('last_id_mf', self.lastline_mf, self.id)
		else:
			djconf.setconfigint('last_id_of', self.lastline_of, self.id)

class schools(list):
	def __init__(self, mtype):
		super().__init__(self)
		if mtype == -1:
			lines = school.objects.filter(active=1)
		else:
			lines = school.objects.filter(active=1, type=mtype)
		for line in lines:
			self.append(oneschool(line.id, line.name, line.type, line.size, line.dir, line.trigger, line.lastclean))

	def get_newline_count(self):
		result = 0
		for oneschool in self:
			result += oneschool.get_newline_count()
		return(result)

	def reset_newline_count(self):
		for oneschool in self:
			oneschool.reset_newline_count()

