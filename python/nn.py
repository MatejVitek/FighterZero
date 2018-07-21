import pickle
import os
import numpy as np
from abc import ABC, abstractmethod

from keras.models import Model, load_model
from keras.layers import Input, Dense, BatchNormalization, LeakyReLU, Dropout
from keras.optimizers import SGD
from keras.regularizers import l2
from keras import backend as K


PATH = '.\\data\\networks\\'
MODEL_EXT = '.h5'
DATA_EXT = '.nn'


class BaseNN(ABC):
	def __init__(self, input_shape, output_sizes):
		self.input_shape = input_shape
		self.output_sizes = output_sizes
		self.model = None
		self._predict = None

	@abstractmethod
	def build(self):
		pass

	def save_weights(self, file):
		print(file, flush=True)
		if '.' not in file[1:]:
			file = file + MODEL_EXT
		if '\\' not in file:
			file = PATH + file
		self.model.save_weights(file)
		print("ASDF", flush=True)

	def load_weights(self, file):
		print(file, flush=True)
		if not self.model:
			self.build()
		if '.' not in file[1:]:
			file = file + MODEL_EXT
		try:
			self.model.load_weights(file)
		except FileNotFoundError:
			self.model.load_weights(PATH + file)
		print("ASDF", flush=True)

	def fit(self, *args, **kwargs):
		return self.model.fit(*args, **kwargs)

	def fast_predict(self, input_vector):
		return self._predict([np.atleast_2d(input_vector)])


class DataBasedNN(BaseNN):
	def __init__(self, input_size, output_size, n_hidden_layers, reg_const, dropout_rate, lr, momentum):
		super().__init__((input_size,), (output_size, 1))
		self.input_size = input_size
		self.output_size = output_size
		self.hidden_layers = n_hidden_layers
		self.regularizer = l2(reg_const)
		self.dropout = dropout_rate
		self.optimizer = SGD(lr=lr, momentum=momentum)

	def build(self):
		x = data_input = Input(self.input_shape, name='data_input')

		step = (self.output_size - self.input_size) / (self.hidden_layers + 1)
		for i in range(1, self.hidden_layers + 1):
			x = self._dense(round(self.input_size + i * step), f'hidden_layer{i}', self.dropout, x)

		policy_out = Dense(
			self.output_size,
			use_bias=False,
			activation='softmax',
			kernel_regularizer=self.regularizer,
			name='policy_output'
		)(x)

		value_condenser = self._dense((self.output_size + 1) // 2, 'value_condenser', 0, x)
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
		if dropout_rate:
			x = Dropout(dropout_rate)(x)
		return x

	def fast_predict(self, input_vector):
		p, v = super().fast_predict(input_vector)
		return p[0], v[0, 0]
