import Settings


class InputVectorBuilder(object):
	def __init__(self, game_data, frame_data, player):
		self.gd = game_data
		self.fd = frame_data
		self.player = player
		self._vector = None

	def build(self):
		self._vector = []
		self._bool(self.player)                                                             # +1

		# FrameData attributes
		self._cont(self.fd.getRemainingFramesNumber(), Settings.ROUND_TIME * Settings.FPS)  # +1
		self._cont(self.fd.getRound(), Settings.ROUNDS, 1)                                  # +1

		# CharacterData attributes
		for p in (self.player, not self.player):
			char = self.fd.getCharacter(p)
			self._disc(char.getAction(), Settings.JVM.enumerate.Action.values())            # +56
			self._cont(char.getCenterX(), self.gd.getStageWidth())                          # +1
			self._cont(char.getCenterY(), self.gd.getStageHeight())                         # +1
			self._cont(char.getEnergy(), self.gd.getMaxEnergy(p))                           # +1
			self._cont(char.getHitCount(), Settings.COMBO_LIMIT)                            # +1
			self._cont(char.getHp(), self.gd.getMaxHP())                                    # +1
			self._cont(char.getRemainingFrame(), Settings.ATT_MAX_FRAMES)                   # +1
			self._cont(char.getSpeedX(), Settings.MAX_SPEEDX, -Settings.MAX_SPEEDX)         # +1
			self._cont(char.getSpeedY(), Settings.MAX_SPEEDY, -Settings.MAX_SPEEDY)         # +1
			self._disc(char.getState(), Settings.JVM.enumerate.State.values())              # +4
			self._bool(char.isControl())                                                    # +1
			self._bool(char.isFront())                                                      # +1

		# Opponent's AttackData attributes
		self._attack_data(self.fd.getCharacter(not self.player).getAttack())

		# Projectile AttackData attributes
		projectiles1, projectiles2 = self.fd.getProjectilesByP1(), self.fd.getProjectilesByP2()
		if not self.player:
			projectiles1, projectiles2 = projectiles2, projectiles1
		for _ in range(Settings.MAX_PROJ):
			self._attack_data(projectiles1.poll())
		for _ in range(Settings.MAX_PROJ):
			self._attack_data(projectiles2.poll())

		assert len(self._vector) == Settings.INPUT_SIZE
		return self._vector

	# AttackData attributes
	def _attack_data(self, att):
		if att is None:
			self._vector.extend([0] * Settings.AD_SIZE)

		self._cont(att.getActive(), Settings.ATT_MAX_FRAMES)                                # +1
		self._disc(att.getAttackType(), (1, 2, 3, 4))                                       # +4
		self._cont(att.getCurrentFrame(), Settings.ATT_MAX_FRAMES)                          # +1
		self._cont(att.getGiveEnergy(), Settings.ATT_MAX_ENERGY)                            # +1
		self._cont(att.getGiveGuardRecov(), Settings.ATT_MAX_GUARD_REC)                     # +1
		self._cont(att.getGuardAddEnergy(), Settings.ATT_MAX_ENERGY)                        # +1
		self._cont(att.getGuardDamage(), Settings.ATT_MAX_DMG)                              # +1
		self._cont(att.getHitAddEnergy(), Settings.ATT_MAX_ENERGY)                          # +1
		self._cont(att.getHitDamage(), Settings.ATT_MAX_DMG)                                # +1
		self._cont(att.getImpactX(), Settings.ATT_MAX_IMPACT)                               # +1
		self._cont(att.getImpactY(), Settings.ATT_MAX_IMPACT, -Settings.ATT_MAX_IMPACT)     # +1
		self._cont(att.getSpeedX(), Settings.MAX_SPEEDX, -Settings.MAX_SPEEDX)              # +1
		self._cont(att.getSpeedY(), Settings.MAX_SPEEDY, -Settings.MAX_SPEEDY)              # +1
		self._cont(att.getStartAddEnergy(), 0, Settings.ATT_MAX_COST)                       # +1
		self._cont(att.getStartUp, Settings.ATT_MAX_FRAMES)                                 # +1
		self._bool(att.isDownProp())                                                        # +1
		self._bool(att.isProjectile())                                                      # +1

		ha = att.getCurrentHitArea()
		self._cont(ha.getBottom(), self.gd.getStageWidth())                                 # +1
		self._cont(ha.getLeft(), self.gd.getStageWidth())                                   # +1
		self._cont(ha.getRight(), self.gd.getStageWidth())                                  # +1
		self._cont(ha.getTop(), self.gd.getStageWidth())                                    # +1

	# Append x to vector, normalizing it from [min, max] to [-1, 1] first
	def _cont(self, x, max, min=0):
		self._vector.append((2 * x - max - min) / (max - min))

	# Append x to vector, transforming it into 1/-1 first for T/F respectively
	def _bool(self, x):
		self._vector.append(1 if x else -1)

	# Append 1 for the class x belongs to and -1 for all other classes.
	def _disc(self, x, all_classes):
		self._vector.extend(1 if x == cls else -1 for cls in all_classes)
