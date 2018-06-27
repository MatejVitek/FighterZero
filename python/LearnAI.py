from keras.models import load_model, Sequential
from keras.layers import Input, Dense

import Settings


class LearnAI(object):
	def __init__(self, gateway):
		self.gateway = gateway

	def initialize(self, gameData, player):
		# Initializng the command center, the simulator and some other things
		self.inputKey = self.gateway.jvm.struct.Key()
		self.frameData = self.gateway.jvm.struct.FrameData()
		self.cc = self.gateway.jvm.aiinterface.CommandCenter()

		self.player = player
		self.gameData = gameData
		self.simulator = self.gameData.getSimulator()

		self.nn = self._build_new_nn() if Settings.INI_FILES[Settings.PLAYER] is None else self._init_nn_from_file()

		return 0

	def getInformation(self, frameData):
		# Getting the frame data of the current frame
		self.frameData = frameData
		self.cc.setFrameData(self.frameData, self.player)

	def processing(self):
		# Just compute the input for the current frame
		if self.frameData.getEmptyFlag() or self.frameData.getRemainingFramesNumber() <= 0:
			self.isGameJustStarted = True
			return

		if self.cc.getSkillFlag():
			self.inputKey = self.cc.getSkillKey()
			return

		self.inputKey.empty()
		self.cc.skillCancel()

		# Just spam kick
		self.cc.commandCall("B")

	def input(self):
		# Return the input for the current frame
		return self.inputKey

	# please define this method when you use FightingICE version 3.20 or later
	def roundEnd(self, x, y, z):
		print(x)
		print(y)
		print(z)

	def close(self):
		if Settings.SAVE_FILES[Settings.PLAYER] is not None:
			self.nn.save(Settings.SAVE_FILES[Settings.PLAYER])

	def _build_new_nn(self):
		nn = Sequential()



		return nn

	def _init_nn_from_file(self):
		return load_model(Settings.INI_FILES[Settings.PLAYER])

	# please define this method when you use FightingICE version 4.00 or later
	def getScreenData(self, sd):
		pass

	# This part is mandatory
	class Java:
		implements = ["aiinterface.AIInterface"]
