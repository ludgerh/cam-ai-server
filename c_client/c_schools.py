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

from c_client.models import school, trainframe, tag
from django.db.models import Max
from .c_tools import classes_list

catfilterdict = {}
for i in range(len(classes_list)):
	catfilterdict['c'+str(i)] = 0

def get_newline_count(myschool, filter):
  maxline = trainframe.objects.filter(school=myschool.id, checked=1).aggregate(Max('id'))
  lastline = maxline['id__max']
  schoolline = school.objects.get(id=myschool.id)
  if (lastline is None):
    lastline = 0
  if filter:
    myschool.lastline_mf = lastline
    before = schoolline.last_id_mf
  else:
    myschool.lastline_of = lastline
    before = schoolline.last_id_of
  filterdict = {'school':myschool.id, 'checked':1, 'id__gt':before}
  result = trainframe.objects.filter(**filterdict)
  if filter:
    result = result.exclude(**catfilterdict)
  return(result.count())

def reset_newline_count(myschool, filter):
  schoolline = school.objects.get(id=myschool.id)
  if filter:
    schoolline.last_id_mf = myschool.lastline_mf
  else:
    schoolline.last_id_of = myschool.lastline_of
  schoolline.save()

def get_taglist(myschool):
  taglist = list(tag.objects.filter(school = 1))
  if myschool > 1:
    extralist = tag.objects.filter(school = myschool)
    for item in extralist:
      taglist[item.replaces].name = item.name 
      taglist[item.replaces].description = item.description
  return(taglist)
