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

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/trdbutil/$', consumers.TrainDBUtilConsumer.as_asgi()),
    re_path(r'ws/scdbutil/$', consumers.SchoolDBUtilConsumer.as_asgi()),
    re_path(r'ws/c_view/$', consumers.c_viewConsumer.as_asgi()),
    re_path(r'ws/trigger/$', consumers.triggerConsumer.as_asgi()),
    re_path(r'ws/oneitem/$', consumers.oneitemConsumer.as_asgi()),
    re_path(r'ws/repeater/$', consumers.repeaterConsumer.as_asgi()),
    re_path(r'ws/repeater/data/$', consumers.repeaterCamConsumer.as_asgi()),
    re_path(r'ws/predictions/$', consumers.predictionsConsumer.as_asgi()),
]
