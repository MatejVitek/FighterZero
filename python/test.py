import Settings
from nn import InputBuilder


def test():
	gd = GameData()
	fd = FrameData()
	print(InputBuilder(gd, fd, True).build())


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
		return Settings.JVM.enumerate.State.STAND if self.p else Settings.JVM.enumerate.State.CROUCH

	def isFront(self):
		return self.p
