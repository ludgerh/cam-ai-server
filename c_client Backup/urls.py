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

from django.urls import path

from . import views

urlpatterns = [
	path('logout/', views.logout_view, name='logout_view'),
	path('', views.cam_index, name='cam_index'),
	path('cams/', views.cam_index, name='cam_index'),
	path('onecam/<int:camnr>/', views.onecam, name='onecam_get'),
	path('detectors/', views.detector_index, name='detector_index'),
	path('onedetector/<int:detectornr>/', views.onedetector, name='onedetector'),
	path('eventers/', views.eventer_index, name='eventer_index'),
	path('oneeventer/<int:eventernr>/', views.oneeventer, name='oneeventer'),
	path('check/', views.check, name='check'),
	path('oneschool/<int:schoolnr>/', views.oneschool, name='oneschool'),
	path('stats/', views.stats, name='stats'),
	path('statsdetails/<int:fitnr>/', views.statdetails, name='statdetails'),
	path('getbmp/<int:model>/<str:name>/', views.getbmp, name='getbmp'),
	path('getmp4/<str:name>/', views.getmp4, name='getmp4'),
	path('getjpg/<int:c_id>/<int:counter>/', views.getjpg, name='getjpg'),
	path('c_canvas/<int:c_viewnr>/<str:mode>/<int:idx>/', views.c_canvas, name='c_canvas'),
	path('camtest/', views.camtest, name='camtest'),
	path('eventlist/<int:schoolnr>/', views.eventlist, name='eventlist'),
]

