import numpy as np
import os, subprocess

from keras.models import Model
from keras.layers import Input, Dense

from py4j.java_gateway import JavaGateway, GatewayParameters as GParams, CallbackServerParameters as CSParams
import settings
from main import JAVA_CMD
from nn import DataBasedNN
from mcts import MCTS


def test():
	gd = settings.JVM.struct.GameData()
	fd = FrameData()
	nn = DataBasedNN(
		input_size=settings.INPUT_SIZE,
		output_size=len(settings.ALL_MOVES),
		n_hidden_layers=settings.HIDDEN_LAYERS,
		reg_const=settings.REG_CONST,
		dropout_rate=settings.DROPOUT_RATE,
		lr=settings.LEARNING_RATE,
		momentum=settings.MOMENTUM
	)
	nn.build()
	nn.save_weights('MyNN.h5')
	in_v = InputBuilder().build('asdf')
	print(nn.fast_predict(in_v))
	settings.TIME_LIMIT = 5
	mcts = MCTS(Simulator(), nn, InputBuilder())
	mcts.search(FrameData(), in_v, True)
	print(mcts)


class GameData(object):
	def __init__(self):
		pass

	def getStageWidth(self):
		return 960

	def getStageHeight(self):
		return 640

	def getMaxEnergy(self, p):
		return 100

	def getMaxHP(self):
		return 100


class FrameData(object):
	def __init__(self):
		pass

	def getRemainingFramesNumber(self):
		return 2500

	def getRound(self):
		return 2

	def getCharacter(self, p):
		return Character(p)


class Character(object):
	def __init__(self, p):
		self.p = p

	def getCenterX(self):
		return 100 if self.p else 500

	def getCenterY(self):
		return 320 if self.p else 160

	def getEnergy(self):
		return 50 if self.p else 10

	def getHitCount(self):
		return 20 if self.p else 0

	def getHp(self):
		return 94 if self.p else 81

	def getRemainingFrame(self):
		return 3 if self.p else 10

	def getSpeedX(self):
		return -10 if self.p else 14

	def getSpeedY(self):
		return 20 if self.p else 0

	def getState(self):
		return 'AIR' if self.p else 'STAND'

	def isFront(self):
		return self.p


class Simulator(object):
	def __init__(self):
		pass

	def simulate(self, state, player, actions1, actions2, frames):
		return FrameData()


class InputBuilder(object):
	def __init__(self):
		pass

	def build(self, state):
		arr = [np.random.random() for _ in range(settings.INPUT_SIZE)]
		return np.array(arr)


def start_java_server():
	print("Starting Java server...")
	os.chdir('..\\')
	return subprocess.Popen(JAVA_CMD + settings.JAVA_ARGS, stdout=subprocess.PIPE, universal_newlines=True)


def wait_for_server():
	print("Waiting for Java server to finish initialisation...")
	while True:
		line = server.stdout.readline().strip()
		if server.poll() is not None and line == '':
			return False
		if line == 'INIT_DONE':
			return True
		print(line)


def close_gateway():
	gateway.close_callback_server()
	gateway.close()


def close_server():
	server.kill()


def main():
	if wait_for_server():
		settings.JVM = gateway.jvm
		test()


if __name__ == '__main__':
	server = start_java_server()
	gateway = JavaGateway(gateway_parameters=GParams(port=settings.PORT), callback_server_parameters=CSParams())
	manager = gateway.entry_point
	try:
		main()
	finally:
		close_gateway()
		close_server()
