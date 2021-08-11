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

from tensorflow.keras.regularizers import l2
from tensorflow.keras.constraints import max_norm
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import BatchNormalization, InputLayer, Conv2D, MaxPool2D, Flatten, Dense, Dropout


def train_once(myschool, allschools):
	seed()
	xdim = djconf.getconfigint('tr_xdim', 331)
	ydim = djconf.getconfigint('tr_ydim', 331)
	epochs = djconf.getconfigint('tr_epochs', 1000)
	batchsize = djconf.getconfigint('tr_batchsize', 32)
	val_split = djconf.getconfigfloat('validation_split', 0.33333333)
	l_rate = djconf.getconfigfloat('learning_rate', 0.0001)
	weight_decay = djconf.getconfigfloat('weight_decay', None)
	dropout = djconf.getconfigfloat('dropout', None)
	weight_constraint = djconf.getconfigfloat('weight_constraint', None)
	mypatience = djconf.getconfigint('patience', 10)
	batch_normalisation = djconf.getconfigbool('batch_normalisation', False)
	
	description = "xdim: " + str(xdim) + "  ydim: " + str(ydim)
	description += "  epochs: " + str(epochs) + "  batchsize: " + str(batchsize)
	description += ("  val_split: " + str(val_split) + "  learning rate: "
		+ str(l_rate)) + "\n" 
	description += ("  weight_decay: " + str(weight_decay) 
		+ "  weight_constraint: " + str(weight_constraint))
	description += ("  dropout: " + str(dropout) + "  patience: " 
		+ str(mypatience))
	description += ("  batch_norm: " + str(batch_normalisation))


	else :
		print('*** Building new model...');
		if weight_decay is None:
			decay_reg = None
		else:
			decay_reg = l2(weight_decay)
		if weight_constraint is None:
			weight_norm = None
		else:
			weight_norm = max_norm(weight_constraint)

		from tensorflow.keras.applications.nasnet import NASNetLarge

		model = Sequential()
		base_model = NASNetLarge(weights='imagenet', include_top=False, 
			input_shape=(ydim, xdim, 3))
		base_model.trainable = False
		model.add(base_model)

		model.add(Flatten())

		model.add(Dense(128,activation="relu", 
			kernel_regularizer=decay_reg, bias_regularizer=decay_reg, 
			kernel_constraint=weight_norm, bias_constraint=weight_norm))
		if dropout is not None:
			model.add(Dropout(dropout))

		model.add(Dense(64,activation="relu", 
			kernel_regularizer=decay_reg, bias_regularizer=decay_reg, 
			kernel_constraint=weight_norm, bias_constraint=weight_norm))
		if dropout is not None:
			model.add(Dropout(dropout))

		model.add(Dense(len(classes_list), activation='sigmoid'))

		model.compile(loss='binary_crossentropy',
			optimizer=Adam(learning_rate=l_rate),
			metrics=[hit100, cmetrics])

		description += """
*** Compile ***
		model.compile(loss='binary_crossentropy',
			optimizer=Adam(learning_rate=l_rate),
			metrics=[hit100, cmetrics])
"""
