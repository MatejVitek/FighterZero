import os
import numpy as np
from abc import ABC, abstractmethod

from keras.models import Model
from keras.layers import Input, Dense, Conv2D, Add, BatchNormalization, LeakyReLU, Dropout, Flatten, Reshape
from keras.optimizers import SGD
from keras.regularizers import l2
from keras import backend as K

import settings


DEF_EXT = '.h5'


class BaseNN(ABC):
	def __init__(self):
		self.model = None
		self._predict = None

	@abstractmethod
	def build(self):
		pass

	def save_weights(self, file):
		name, ext = os.path.splitext(file)
		if not ext:
			ext = DEF_EXT
		self.model.save_weights(name + ext)

	def load_weights(self, file):
		if not self.model:
			self.build()
		name, ext = os.path.splitext(file)
		if not ext:
			ext = DEF_EXT
		self.model.load_weights(name + ext)

	def fit(self, training_samples, *args, **kwargs):
		input_vectors, ps, vs = tuple(np.asarray(x) for x in zip(*training_samples))
		self.model.fit(x=input_vectors, y=[ps, vs], *args, **kwargs)

	def predict(self, input_):
		return self._predict([input_])


class DataNN(BaseNN):
	def __init__(self):
		super().__init__()
		self.regularizer = l2(settings.REG_CONST)
		self.optimizer = SGD(lr=settings.LEARNING_RATE, momentum=settings.MOMENTUM)

	def build(self):
		in_size = settings.INPUT_SIZE
		out_size = len(settings.ALL_MOVES)
		hidden = settings.HIDDEN_LAYERS

		x = data_input = Input((in_size,), name='data_input')

		step = (out_size - in_size) / (hidden + 1)
		for i in range(1, hidden + 1):
			x = self._dense(round(in_size + i * step), f'hidden_layer{i}', settings.DROPOUT_RATE, x)

		policy_out = Dense(
			out_size,
			use_bias=False,
			activation='softmax',
			kernel_regularizer=self.regularizer,
			name='policy_output'
		)(x)

		value_condenser = self._dense((out_size + 1) // 2, 'value_condenser', 0, x)
		value_out = Dense(
			1,
			use_bias=False,
			activation='tanh',
			kernel_regularizer=self.regularizer,
			name='value_output'
		)(value_condenser)

		self.model = Model(inputs=[data_input], outputs=[policy_out, value_out])
		self.model.compile(
			optimizer=self.optimizer,
			loss={'policy_output': 'categorical_crossentropy', 'value_output': 'mean_squared_error'},
			loss_weights={'policy_output': 0.6, 'value_output': 0.4}
		)
		self._predict = K.function([data_input], [policy_out, value_out])

	def _dense(self, size, name, dropout_rate, previous):
		x = Dense(
			size,
			use_bias=False,
			activation='linear',
			kernel_regularizer=self.regularizer,
			name=name
		)(previous)
		x = BatchNormalization(axis=1)(x)
		x = LeakyReLU()(x)
		return Dropout(dropout_rate)(x) if dropout_rate else x

	def predict(self, input_vector):
		p, v = super().predict(np.array(input_vector, copy=False, ndmin=2))
		return p[0], v[0, 0]


class ImageNN(BaseNN):
	def __init__(self):
		super().__init__()
		self.regularizer = l2(settings.REG_CONST)
		self.optimizer = SGD(lr=settings.LEARNING_RATE, momentum=settings.MOMENTUM)

	def build(self):
		in_shape = (settings.IMAGE_HEIGHT, settings.IMAGE_WIDTH)
		out_size = len(settings.ALL_MOVES)
		residual = settings.RES_LAYERS

		x = image_input = Input(in_shape, name='image_input')
		x = Reshape((1,) + in_shape, name='input_reshape')(x)

		x = self._conv(settings.FIRST_FILTER_SIZE, 'input_conv', x)

		for i in range(1, residual + 1):
			x = self._residual(i, x)

		policy_conv = self._conv(1, 'policy_conv', x, channels=2, flatten=True)
		policy_out = Dense(
			out_size,
			use_bias=False,
			activation='softmax',
			kernel_regularizer=self.regularizer,
			name='policy_output'
		)(policy_conv)

		value_conv = self._conv(1, 'value_conv', x, channels=4, flatten=True)
		value_condenser = Dense(
			(out_size + 1) // 2,
			use_bias = False,
			activation='relu',
			kernel_regularizer=self.regularizer,
			name='value_condenser'
		)(value_conv)
		value_out = Dense(
			1,
			use_bias=False,
			activation='tanh',
			kernel_regularizer=self.regularizer,
			name='value_output'
		)(value_condenser)

		self.model = Model(inputs=[image_input], outputs=[policy_out, value_out])
		self.model.compile(
			optimizer=self.optimizer,
			loss={'policy_output': 'categorical_crossentropy', 'value_output': 'mean_squared_error'},
			loss_weights={'policy_output': 0.6, 'value_output': 0.4}
		)

		self._predict = K.function([image_input], [policy_out, value_out])

	def _conv(self, filter_size, name, previous, channels=settings.CHANNELS, activation=True, flatten=False):
		x = Conv2D(
			filters=channels,
			kernel_size=filter_size,
			padding='same',
			data_format='channels_first',
			use_bias=False,
			kernel_regularizer=self.regularizer,
			name=name
		)(previous)
		x = BatchNormalization(axis=1, name=f'{name}_norm')(x)
		if activation:
			x = LeakyReLU(name=f'{name}_act')(x)
		if flatten:
			x = Flatten(name=f'{name}_flat')(x)
		return x

	def _residual(self, i, previous):
		x = self._conv(settings.FILTER_SIZE, f'res{i}_conv1', previous)
		x = self._conv(settings.FILTER_SIZE, f'res{i}_conv2', x, activation=False)
		x = Add(name=f'res{i}_add')([previous, x])
		return LeakyReLU(name=f'res{i}_act')(x)

	def predict(self, input_matrix):
		p, v = super().predict(np.array(input_matrix, copy=False, ndmin=3))
		return p[0], v[0, 0]
