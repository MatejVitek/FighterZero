from keras.models import Model, load_model
from keras.layers import Input, Dense, LeakyReLU
from keras.optimizers import SGD
from keras.regularizers import l2


class BaseNN(object):
	def __init__(self, input_shape, output_sizes, reg_const, learning_rate, momentum):
		self.input_shape = input_shape
		self.output_sizes = output_sizes
		self.regularizer = l2(reg_const)
		self.optimizer = SGD(lr=learning_rate, momentum=momentum)
		self.model = None

	def build(self):
		main_input = Input(self.input_shape)
		main_output = Dense(sum(self.output_sizes))(main_input)

		self.model = Model(inputs=[main_input], outputs=[main_output])
		self.model.compile(self.optimizer)

		return self.model

	def save(self, file):
		if '\\' not in file:
			file = '.\\data\\networks\\' + file
		self.model.save(file)

	def load(self, file):
		try:
			self.model = load_model(file)
		except FileNotFoundError:
			self.model = load_model('.\\data\\networks\\' + file)
		return self.model


class DataBasedNN(BaseNN):
	def __init__(self, input_size, ground_output_size, air_output_size, n_hidden_layers, *args, **kwargs):
		super().__init__((input_size,), (ground_output_size, air_output_size), *args, **kwargs)
		self.input_size = input_size
		self.output_size = {'ground': ground_output_size, 'air': air_output_size}
		self.hidden_layers = n_hidden_layers

	def build(self):
		x = data_input = Input(self.input_shape, name='data_input')

		step = (sum(self.output_sizes) - self.input_size) / (self.hidden_layers + 1)
		for i in range(1, self.hidden_layers + 1):
			x = self.dense(round(self.input_size + i * step), f'hidden_layer{i}', x)

		outputs = []
		for state in 'ground', 'air':
			value_condenser = self.dense((self.output_size[state] + 1) // 2, f'{state}_value_condenser', x)
			outputs.append(Dense(
			    1,
			    use_bias=False,
			    activation='tanh',
			    kernel_regularizer=self.regularizer,
			    name=f'{state}_value_output'
			)(value_condenser))

			outputs.append(self.dense(self.output_size[state], f'{state}_policy_output', x, False))

		self.model = Model(inputs=[data_input], outputs=outputs)

		losses = {f'{state}_{type_}_output': loss
		          for state in ('ground', 'air')
		          for type_, loss in zip(('value', 'policy'), ('mean_squared_error', 'categorical_crossentropy'))}
		loss_weights = {f'{state}_{type_}_output': weight
		                for state in ('ground', 'air')
		                for type_, weight in zip(('value', 'policy'), (0.2, 0.3))}
		self.model.compile(self.optimizer, loss=losses, loss_weights=loss_weights)

	def dense(self, size, name, previous, activator=True):
		x = Dense(
			size,
			use_bias=False,
			activation='linear',
			kernel_regularizer=self.regularizer,
			name=name
		)(previous)
		return LeakyReLU(x) if activator else x