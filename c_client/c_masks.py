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
import cv2 as cv
from shapely.geometry import Point, LinearRing

class mask_list(list):
	def __init__(self, intlist, xscaling=1, yscaling=1):
		super().__init__()
		for mypoints in intlist:
			mypoints = [[mypoint[0]*xscaling, mypoint[1]*yscaling] 
				for mypoint in mypoints]
			self.append(mypoints)

	def new_ring(self, x, y):
		mymask = [[x/2-50,y/2-50], [x/2-50,y/2], [x/2-50,y/2+50], [x/2,y/2+50], 
			[x/2+50,y/2+50], [x/2+50,y/2], [x/2+50,y/2-50], [x/2,y/2-50]]
		self.append(mymask)

	def ints_from_mask(self, x, y, xorig, yorig):
		result1 = []
		for ring in self:
			result2 = []
			for item in ring:
				result3 = []
				if round(item[0]) >= (x - 1):
					result3.append(xorig - 1)
				else:
					result3.append(round(item[0] * xorig / x))
				if round(item[1]) >= (y - 1):
					result3.append(yorig - 1)
				else:
					result3.append(round(item[1] * yorig / y))
				result2.append(result3)
			result1.append(result2)
		result1 = mask_list(result1)
		return(result1)

	def draw_rings(self, drawpad, foregr, radius):
		for ring in self:
			pts = np.array(ring, np.int32)
			cv.polylines(drawpad,[pts],True,foregr,2) 
			for item in ring:
				cv.circle(drawpad,(round(item[0]),round(item[1])),
					radius,foregr, -1)

	def point_clicked(self, x, y, radius):
		click_point = Point(x,y) 
		for i in range(len(self)):
			for j in range(len(self[i])):
				check_point = Point(self[i][j])
				if check_point.distance(click_point) <= radius:
					return((i,j))
		return(None)

	def move_point(self, mypoint, x, y, drawpad, foregr, radius):
		buffer = self[mypoint[0]][mypoint[1]]
		self[mypoint[0]][mypoint[1]] = (x, y)
		testring = LinearRing(self[mypoint[0]])
		if (testring.is_valid) and (testring.is_simple):
			self.draw_rings(drawpad, foregr, radius)
		else:
			self[mypoint[0]][mypoint[1]] = buffer

	def mask_from_polygons(self, x, y, backgr, foregr):
		result = np.zeros((y, x, 3), np.uint8)
		result[:] = backgr
		for polygon in self:
			polygon = np.array(polygon).round().astype(np.int32)
			cv.fillPoly(result, [polygon], foregr)
		return(result)

	def make_drawpad(self, x, y, backgr, foregr, radius):
		result = np.zeros((y, x, 3), np.uint8)
		result[:] = backgr
		self.draw_rings(result, foregr, radius)
		return(result)


