import settings
from settings import P

import numpy as np
import matplotlib.pyplot as plot


class DrawAI(object):
	def __init__(self, gateway):
		self.gateway = gateway

	def close(self):
		pass

	def getInformation(self, frameData):
		# Getting the frame data of the current frame
		self.frameData = frameData
		self.cc.setFrameData(self.frameData, self.player)

	# please define this method when you use FightingICE version 3.20 or later
	def roundEnd(self, x, y, z):
		print(x)
		print(y)
		print(z)

	# please define this method when you use FightingICE version 4.00 or later
	def getScreenData(self, sd):
		self.screenData = sd

	def initialize(self, gameData, player):
		# Initializng the command center, the simulator and some other things
		self.inputKey = self.gateway.jvm.struct.Key()
		self.frameData = self.gateway.jvm.struct.FrameData()
		self.cc = self.gateway.jvm.aiinterface.CommandCenter()

		self.player = player
		self.gameData = gameData
		self.simulator = self.gameData.getSimulator()

		return 0

	def input(self):
		# Return the input for the current frame
		return self.inputKey

	def processing(self):
		try:
			# Just compute the input for the current frame
			if self.frameData.getEmptyFlag() or self.frameData.getRemainingFramesNumber() <= 0:
				self.isGameJustStarted = True
				return

			if self.isGameJustStarted:
				self.isGameJustStarted = False
				actions1 = self.gateway.jvm.java.util.ArrayDeque()
				actions1.add(self.gateway.jvm.enumerate.Action.DASH)
				actions1.add(self.gateway.jvm.enumerate.Action.STAND_D_DB_BA)
				actions1.add(self.gateway.jvm.enumerate.Action.STAND_B)
				actions1.add(self.gateway.jvm.enumerate.Action.STAND_A)
				actions2 = self.gateway.jvm.java.util.ArrayDeque()
				actions2.add(self.gateway.jvm.enumerate.Action.BACK_JUMP)
				actions2.add(self.gateway.jvm.enumerate.Action.AIR_D_DB_BA)
				actions2.add(self.gateway.jvm.enumerate.Action.AIR_B)
				actions2.add(self.gateway.jvm.enumerate.Action.AIR_A)
				new_fd = self.simulator.simulate(self.frameData, self.player, actions1, actions2, 12)

				old_screen = self.build(self.screenData)
				new_screen = self.simulate(old_screen, self.frameData, new_fd)

				print("Saving images")

				plot.imsave('Sim1.png', old_screen, vmin=-1.0, vmax=1.0, cmap=plot.cm.gray)
				plot.imsave('Sim2.png', new_screen, vmin=-1.0, vmax=1.0, cmap=plot.cm.gray)

			if self.cc.getSkillFlag():
				self.inputKey = self.cc.getSkillKey()
				return

			self.inputKey.empty()
			self.cc.skillCancel()

			# Just spam kick
			self.cc.commandCall("B")

		except BaseException as e:
			print(f"PROCESSING ERROR: {e.args}", flush=True)
			raise e

	@staticmethod
	def build(sd):
		# print("B1", time.perf_counter(), flush=True)
		display_buffer = sd.getDisplayByteBufferAsBytes(settings.IMAGE_WIDTH, settings.IMAGE_HEIGHT, True)
		# print("B2", time.perf_counter(), flush=True)
		screen = np.frombuffer(display_buffer, dtype=np.int8)
		# print("B3", time.perf_counter(), flush=True)
		screen = screen.reshape(settings.IMAGE_HEIGHT, settings.IMAGE_WIDTH)
		# print("B4", time.perf_counter(), flush=True)
		screen = screen / 127.  # Can't do screen /= 127. because of read-only error
		# print("B5", time.perf_counter(), flush=True)
		return screen.astype(np.float32)

	@staticmethod
	def simulate(old_sd, old_fd, new_fd):
		new_sd = old_sd.copy()

		old_c = {p: old_fd.getCharacter(p) for p in P}
		new_c = {p: new_fd.getCharacter(p) for p in P}

		ratio_x = settings.IMAGE_WIDTH / settings.STAGE_WIDTH
		ratio_y = settings.IMAGE_HEIGHT / settings.STAGE_HEIGHT

		# HP bars
		y_start = int(75 * ratio_y)
		y_end = int(95 * ratio_y)
		for p, step in zip(P, (-1, 1)):
			x_start = int((480 + step * (50 + new_c[p].getHp() / settings.HP[p] * 300)) * ratio_x)
			x_end = int((480 + step * (50 + old_c[p].getHp() / settings.HP[p] * 300)) * ratio_x)
			for y in range(y_start, y_end):
				for x in range(x_start, x_end, step):
					new_sd[y, x] = 0.2 * 2 - 1

		# Characters
		for p in P:
			old_cx = old_c[p].getCenterX()
			old_cy = old_c[p].getCenterY()
			new_cx = new_c[p].getCenterX()
			new_cy = new_c[p].getCenterY()
			old_left = max(int((old_cx - 100) * ratio_x), 0)
			old_right = min(int((old_cx + 100) * ratio_x), settings.IMAGE_WIDTH)
			old_top = max(int((old_cy - 100) * ratio_y), 0)
			old_bot = min(int((old_cy + 100) * ratio_y), settings.IMAGE_HEIGHT)
			new_left = max(int((new_cx - 100) * ratio_x), 0)
			new_right = min(int((new_cx + 100) * ratio_x), settings.IMAGE_WIDTH)
			new_top = max(int((new_cy - 100) * ratio_y), 0)
			new_bot = min(int((new_cy + 100) * ratio_y), settings.IMAGE_HEIGHT)

			# Move character
			for old_y, new_y in zip(range(old_top, old_bot), range(new_top, new_bot)):
				# Make sure we're not overwriting or copying HP bar data
				if y_start <= old_y <= y_end or y_start <= new_y <= y_end:
					continue
				for old_x, new_x in zip(range(old_left, old_right), range(new_left, new_right)):
					new_sd[new_y, new_x] = new_sd[old_y, old_x]

			# Remove vertical artifact
			artifact_left = new_right if new_cx < old_cx else old_left
			artifact_right = old_right if new_cx < old_cx else new_left
			for y in range(old_top, old_bot):
				if y_start <= y <= y_end:
					continue
				for x in range(artifact_left, artifact_right):
					new_sd[y, x] = 0.

			# Remove horizontal artifact
			artifact_top = new_bot if new_cy < old_cy else old_top
			artifact_bot = old_bot if new_cy < old_cy else new_top
			artifact_left = new_left if new_cy < old_cy else old_left
			artifact_right = old_right if new_cy < old_cy else new_right
			for y in range(artifact_top, artifact_bot):
				if y_start <= y <= y_end:
					continue
				for x in range(artifact_left, artifact_right):
					new_sd[y, x] = 0.

		return new_sd

	# This part is mandatory
	class Java:
		implements = ["aiinterface.AIInterface"]

