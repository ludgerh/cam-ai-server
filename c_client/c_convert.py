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

import cv2 as cv
import numpy as np

# Frame Types:
# 1 : Jpeg Data
# 2 : Pillow Data
# 3 : opencv Data

def c_convert(inframe, typein=None, typeout=None, xout=None, yout=None):
	if xout:
		if typein == 3:
			xin = inframe.shape[1]
			yin = inframe.shape[0]
		if xin != xout:
			if not yout:
				yout = round(yin / xin * xout)
			inframe = cv.resize(inframe, (xout, yout))
	if typein and typeout and (typein != typeout):
		if typein == 1:
			if typeout == 3:
				inframe = cv.imdecode(np.fromstring(inframe, dtype=np.uint8), cv.IMREAD_UNCHANGED)
		elif typein == 3:
			if typeout == 1:
				inframe = cv.imencode('.jpg', inframe)[1].tostring()
	return(inframe)

