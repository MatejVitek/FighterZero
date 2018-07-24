import numpy as np
import time

import settings


class InputBuilder(object):
	def __init__(self, game_data, player):
		self.player = player

		# self.actions = tuple(settings.JVM.enumerate.Action.values())
		# self.states = tuple(settings.JVM.enumerate.State.values())
		self.stage_width = game_data.getStageWidth()
		self.stage_height = game_data.getStageHeight()
		self.max_energy = {p: game_data.getMaxEnergy(p) for p in settings.P}
		self.max_hp = {p: game_data.getMaxHP(p) for p in settings.P}

		if settings.NN == 'DataNN':
			self.build = self._build_from_data
			self.build_random = lambda: np.random.rand(1, settings.INPUT_SIZE)
			self.symmetrical = self._symmetrical_data
		elif settings.NN == 'ImageNN':
			self.build = self._build_from_image
			self.build_random = lambda: np.random.randint(256, size=(settings.IMAGE_HEIGHT, settings.IMAGE_WIDTH))
		else:
			raise ValueError("Invalid NN type.")

	def _build_from_data(self, state):
		# print("B1", time.perf_counter(), flush=True)
		self._vector = np.empty(settings.INPUT_SIZE, dtype=float)
		self._i = 0
		# print("B2", time.perf_counter(), flush=True)

		# CharacterData attributes
		for p in (self.player, not self.player):
			# print("B3", time.perf_counter(), flush=True)
			char = state.getCharacter(p)
			# print("B4", time.perf_counter(), flush=True)
			self._cont(char.getCenterX(), self.stage_width)
			self._cont(char.getCenterY(), self.stage_height)
			self._cont(char.getHp(), self.max_hp[p])
			self._cont(char.getEnergy(), self.max_energy[p])
			# print("B5", time.perf_counter(), flush=True)

		assert self._i == settings.INPUT_SIZE
		# print("B6", time.perf_counter(), flush=True)
		return self._vector

	# Append x after normalizing it from [min, max] to [-1, 1] first
	def _cont(self, x, max, min=0.):
		self._append((2. * x - max - min) / (max - min))

	# Append 1/-1 for T/F respectively
	def _bool(self, x):
		self._append(1. if x else -1.)

	# Append 1 for the class x belongs to and -1 for all other classes.
	def _disc(self, x, all_classes):
		class_i = self._i + all_classes.index(x)
		self._extend(-1, len(all_classes))
		self._vector[class_i] = 1

	# Append x to vector
	def _append(self, x):
		self._vector[self._i] = x
		self._i += 1

	# Append x to vector n times
	def _extend(self, x, n):
		self._vector[self._i:self._i+n] = x
		self._i += n

	def _symmetrical_data(self, vector):
		sym = vector.copy()
		sym[0:2] = -sym[0:2]
		sym[3:4] = -sym[3:4]
		return sym

	def _build_from_image(self, sd):
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

	def _build_full(self, state):
		# print("B1", time.perf_counter(), flush=True)
		self._vector = np.empty(settings.INPUT_SIZE, dtype=float)
		self._i = 0
		self._bool(self.player)                                                             # +1
		# print("B2", time.perf_counter(), flush=True)

		# FrameData attributes
		self._cont(state.getRemainingFramesNumber(), settings.ROUND_TIME * settings.FPS)    # +1
		self._cont(state.getRound(), settings.ROUNDS, 1)                                    # +1
		# print("B3", time.perf_counter(), flush=True)

		# CharacterData attributes
		for p in (self.player, not self.player):
			# print("B4", time.perf_counter(), flush=True)
			char = state.getCharacter(p)
			# print("B4.1", time.perf_counter(), flush=True)
			self._disc(char.getAction(), self.actions)                                      # +56
			# print("B5", time.perf_counter(), flush=True)
			self._cont(char.getCenterX(), self.stage_width)                                 # +1
			self._cont(char.getCenterY(), self.stage_height)                                # +1
			self._cont(char.getEnergy(), self.max_energy[p])                                # +1
			self._cont(char.getHitCount(), settings.COMBO_LIMIT)                            # +1
			self._cont(char.getHp(), self.max_hp[p])                                        # +1
			self._cont(char.getRemainingFrame(), settings.ATT_MAX_FRAMES)                   # +1
			self._cont(char.getSpeedX(), settings.MAX_SPEEDX, -settings.MAX_SPEEDX)         # +1
			self._cont(char.getSpeedY(), settings.MAX_SPEEDY, -settings.MAX_SPEEDY)         # +1
			# print("B6", time.perf_counter(), flush=True)
			self._disc(char.getState(), self.states)                                        # +4
			# print("B7", time.perf_counter(), flush=True)
			self._bool(char.isControl())                                                    # +1
			self._bool(char.isFront())                                                      # +1
			# print("B8", time.perf_counter(), flush=True)

		# Opponent's AttackData attributes
		self._attack_data(state.getCharacter(not self.player).getAttack())
		# print("B9", time.perf_counter(), flush=True)

		# Projectile AttackData attributes
		projectiles1, projectiles2 = state.getProjectilesByP1(), state.getProjectilesByP2()
		# print("B10", time.perf_counter(), flush=True)
		if not self.player:
			projectiles1, projectiles2 = projectiles2, projectiles1
		for _ in range(settings.MAX_PROJ):
			self._attack_data(projectiles1.poll())
		# print("B11", time.perf_counter(), flush=True)
		for _ in range(settings.MAX_PROJ):
			self._attack_data(projectiles2.poll())
		# print("B12", time.perf_counter(), flush=True)
		assert self._i == settings.INPUT_SIZE
		# print("B13", time.perf_counter(), flush=True)
		return self._vector

	# AttackData attributes
	def _attack_data(self, att):
		if att is None:
			self._extend(0, settings.AD_SIZE)
			return

		self._cont(att.getActive(), settings.ATT_MAX_FRAMES)                                # +1
		self._disc(att.getAttackType(), (0, 1, 2, 3, 4))                                    # +5
		self._cont(att.getCurrentFrame(), settings.ATT_MAX_FRAMES)                          # +1
		self._cont(att.getGiveEnergy(), settings.ATT_MAX_ENERGY)                            # +1
		self._cont(att.getGiveGuardRecov(), settings.ATT_MAX_GUARD_REC)                     # +1
		self._cont(att.getGuardAddEnergy(), settings.ATT_MAX_ENERGY)                        # +1
		self._cont(att.getGuardDamage(), settings.ATT_MAX_DMG)                              # +1
		self._cont(att.getHitAddEnergy(), settings.ATT_MAX_ENERGY)                          # +1
		self._cont(att.getHitDamage(), settings.ATT_MAX_DMG)                                # +1
		self._cont(att.getImpactX(), settings.ATT_MAX_IMPACT)                               # +1
		self._cont(att.getImpactY(), settings.ATT_MAX_IMPACT, -settings.ATT_MAX_IMPACT)     # +1
		self._cont(att.getSpeedX(), settings.MAX_SPEEDX, -settings.MAX_SPEEDX)              # +1
		self._cont(att.getSpeedY(), settings.MAX_SPEEDY, -settings.MAX_SPEEDY)              # +1
		self._cont(att.getStartAddEnergy(), 0, settings.ATT_MAX_COST)                       # +1
		self._cont(att.getStartUp(), settings.ATT_MAX_FRAMES)                               # +1
		self._bool(att.isDownProp())                                                        # +1
		self._bool(att.isProjectile())                                                      # +1

		ha = att.getCurrentHitArea()
		self._cont(ha.getBottom(), self.stage_height)                                       # +1
		self._cont(ha.getLeft(), self.stage_width)                                          # +1
		self._cont(ha.getRight(), self.stage_width)                                         # +1
		self._cont(ha.getTop(), self.stage_height)                                          # +1
