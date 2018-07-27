import numpy as np
import os
import threading

import tensorflow as tf

import settings
import nn
from input import InputBuilder
from mcts import MCTS


class PlayAI(object):
	def __init__(self, ini_file=None):
		self.game_num = 0
		self.game_score = 0

		self.nn = getattr(nn, settings.NN)()
		if ini_file:
			self.nn.load_weights(ini_file)
		else:
			self.nn.build()
		self._graph = tf.get_default_graph()

	def initialize(self, gameData, player):
		try:
			# Initializng the command center, the simulator and some other things
			self.inputKey = settings.JVM.struct.Key()
			self.frameData = settings.JVM.struct.FrameData()
			self.cc = settings.JVM.aiinterface.CommandCenter()

			self.player = player
			self.gameData = gameData
			self.score = 0
			self.game_num += 1
			print(f"Starting game number {self.game_num}.")

			self.input_builder = InputBuilder(self.gameData, self.player)
			os.environ['CUDA_VISIBLE_DEVICES'] = ''

			# Make graph default for session + make a random prediction because the initial prediction can take longer
			with self._graph.as_default():
				self.nn.predict(self.input_builder.build_random())

			self.mcts = MCTS(self.gameData.getSimulator(), self.nn, self.input_builder)
			self.action_thread = None
			self.action = None

		except BaseException as e:
			print(f"INIT ERROR: {e.args}", flush=True)
			raise e

		return 0

	def getInformation(self, fd):
		self.frameData = fd
		self.cc.setFrameData(fd, self.player)

	def getScreenData(self, sd):
		self.screenData = sd

	def processing(self):
		try:
			# Just compute the input for the current frame
			if self.frameData.getEmptyFlag() or self.frameData.getRemainingFramesNumber() <= 0:
				return

			if self.cc.getSkillFlag():
				self.inputKey = self.cc.getSkillKey()
				return

			self.inputKey.empty()
			self.cc.skillCancel()

			if self.action_thread is None:
				self.action_thread = threading.Thread(target=self.find_best_action)
				self.action_thread.start()

			if not self.action_thread.is_alive():
				self.cc.commandCall(self.action)
				self.inputKey = self.cc.getSkillKey()
				self.action_thread = None

		except BaseException as e:
			print(f"PROCESSING ERROR: {e.args}", flush=True)
			raise e

	def find_best_action(self):
		self.action = None
		input_vector = self.input_builder.build(self.frameData if settings.NN == 'DataNN' else self.screenData)
		with tf.device('/cpu:0'):
			p = self.mcts.search(self.frameData, input_vector, self.player, settings.TEMP)
		self.action = settings.ALL_MOVES[np.argmax(p)]

	def input(self):
		# Return the input for the current frame
		return self.inputKey

	# please define this method when you use FightingICE version 3.20 or later
	def roundEnd(self, hp1, hp2, frames):
		try:
			if self.action_thread is not None:
				self.action_thread.join()

			if not self.player:
				hp1, hp2 = hp2, hp1
			self.score += np.sign(hp1 - hp2)

		except BaseException as e:
			print(f"ROUND END ERROR: {e.args}", flush=True)
			raise e

	def close(self):
		self.game_score += np.sign(self.score)
		print(f"Score: {(self.game_num + self.game_score) // 2}-{(self.game_num - self.game_score) // 2}")

	# This part is mandatory
	class Java:
		implements = ["aiinterface.AIInterface"]
