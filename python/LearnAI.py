import numpy as np
import os

import tensorflow as tf

import settings
from input import InputVectorBuilder
from mcts import MCTS
from nn import DataBasedNN


class LearnAI(object):
	def __init__(self):
		self.game_num = 0

	def initialize(self, gameData, player):
		# Initializng the command center, the simulator and some other things
		self.inputKey = settings.JVM.struct.Key()
		self.state = settings.JVM.struct.FrameData()
		self.cc = settings.JVM.aiinterface.CommandCenter()

		self.player = player
		self.gameData = gameData
		self.score = 0
		self.game_num += 1
		print(f"Starting game number {self.game_num}.")

		self.input_builder = InputVectorBuilder(self.gameData, self.player)
		self.nn = DataBasedNN(
			input_size=settings.INPUT_SIZE,
			output_size=len(settings.ALL_MOVES),
			n_hidden_layers=settings.HIDDEN_LAYERS,
			reg_const=settings.REG_CONST,
			dropout_rate=settings.DROPOUT_RATE,
			lr=settings.LEARNING_RATE,
			momentum=settings.MOMENTUM
		)
		if settings.INI_FILES[self.player]:
			self.nn.load_weights(settings.INI_FILES[self.player])
		else:
			self.nn.build()
		os.environ['CUDA_VISIBLE_DEVICES'] = ''
		self.nn.fast_predict(self.input_builder.build_random())

		self.mcts = MCTS(self.gameData.getSimulator(), self.nn, self.input_builder)
		self.training_examples = []

		return 0

	def getInformation(self, state):
		# Getting the frame data of the current frame
		self.state = state
		self.cc.setFrameData(self.state, self.player)

	def processing(self):
		# Just compute the input for the current frame
		remaining_frames = self.state.getRemainingFramesNumber()
		if self.state.getEmptyFlag() or remaining_frames <= 0:
			return

		if self.cc.getSkillFlag():
			self.inputKey = self.cc.getSkillKey()
			return

		self.inputKey.empty()
		self.cc.skillCancel()

		# Stop 15 frames before round end, otherwise might hang when game ends
		if remaining_frames > 15:
			input_vector = self.input_builder.build(self.state)
			with tf.device('/cpu:0'):
				p = self.mcts.search(self.state, input_vector, self.player, settings.TEMP)
			self.training_examples.append([input_vector, p, None])
			self.training_examples.append([self.input_builder.symmetrical(input_vector), p, None])
		else:
			# Otherwise might hang when game ends
			p = np.array([1. / len(settings.ALL_MOVES) for _ in range(len(settings.ALL_MOVES))])
		action = np.random.choice(settings.ALL_MOVES, p=p)

		# Can't call commandCall with getattr'd action, so use strings
		self.cc.commandCall(action)
		self.inputKey = self.cc.getSkillKey()

	def input(self):
		# Return the input for the current frame
		return self.inputKey

	# please define this method when you use FightingICE version 3.20 or later
	def roundEnd(self, hp1, hp2, frames):
		if not self.player:
			hp1, hp2 = hp2, hp1
		self.score += np.sign(hp1 - hp2)

		reward = (hp1 - hp2) * settings.ROUND_REWARD_CONSTANT
		for i in range(len(self.training_examples)):
			self.training_examples[i][2] = reward

	def close(self):
		os.environ['CUDA_VISIBLE_DEVICES'] = '0'
		self.score = np.sign(self.score) * np.sqrt(abs(self.score))
		for i in range(len(self.training_examples)):
			self.training_examples[i][2] += self.score * settings.GAME_REWARD_EXTRA

		if settings.SAVE_FILES[self.player] is not None:
			self.nn.save_weights(settings.SAVE_FILES[self.player])
			settings.INI_FILES[self.player] = settings.SAVE_FILES[self.player]

	# please define this method when you use FightingICE version 4.00 or later
	def getScreenData(self, sd):
		pass

	# This part is mandatory
	class Java:
		implements = ["aiinterface.AIInterface"]
