import Settings
from nn import NNBuilder


class LearnAI(object):
	def __init__(self):
		pass

	def initialize(self, gameData, player):
		# Initializng the command center, the simulator and some other things
		self.inputKey = Settings.JVM.struct.Key()
		self.frameData = Settings.JVM.struct.FrameData()
		self.cc = Settings.JVM.aiinterface.CommandCenter()

		self.player = player
		self.gameData = gameData
		self.simulator = self.gameData.getSimulator()

		ini = Settings.INI_FILES[self.player]
		if ini:
			self.nn = builder.my_nn(Settings.HIDDEN_LAYERS)
		else:
			self.nn = builder.load(ini)

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
		if Settings.SAVE_FILES[self.player] is not None:
			self.nn.save(Settings.SAVE_FILES[self.player])

	# please define this method when you use FightingICE version 4.00 or later
	def getScreenData(self, sd):
		pass

	# This part is mandatory
	class Java:
		implements = ["aiinterface.AIInterface"]
