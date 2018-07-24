import time
import math
import numpy as np

import game
import settings
from settings import P


class MCTS(object):
	def __init__(self, simulator, nn, input_builder):
		self.sim = simulator
		self.nn = nn
		self.input_builder = input_builder
		self.root = None
		self.start = 0

		# Set up JVM stuff, calls to JVM are time-intensive.
		self.action_deque = settings.JVM.java.util.ArrayDeque()
		self.enumerated_actions = {a: getattr(settings.JVM.enumerate.Action, a) for a in settings.ALL_MOVES}
		# Also call each method once randomly, since initial method calls are also time-intensive.
		self.action_deque.add(settings.JVM.enumerate.Action.NEUTRAL)
		self.action_deque.clear()

	def search(self, fd, initial_input_vector, player, temp=1.):
		self.root = Node(fd, player, None, self, initial_input_vector)
		self.start = time.perf_counter()
		while not self.time_expired():
			# print("M1", time.perf_counter(), flush=True)
			self.root.search()

		print(f"Number of MCTS simulations: {self.root.N}", flush=True)
		N = np.array([self.root.edges[action].N if action in self.root.edges else 0 for action in settings.ALL_MOVES])
		N = N.astype(float)

		if all(x == 0. for x in N):
			# print("All probabilities are 0.")
			return np.ones(len(settings.ALL_MOVES)).astype(float) / len(settings.ALL_MOVES)

		try:
			N **= 1. / temp
			P = N / np.sum(N)
		except ZeroDivisionError:
			P = np.zeros(len(settings.ALL_MOVES)).astype(float)
			P[np.argmax(N)] = 1.
		return P

	def time_expired(self):
		return time.perf_counter() - self.start >= settings.TIME_LIMIT

	@staticmethod
	def screen_simulate(old_sd, old_fd, new_fd):
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

	def __str__(self):
		return str(self.root)


class Node(object):
	def __init__(self, fd, player_on_the_move, parent, mcts, input_vector=None):
		self.fd = fd
		self.player = player_on_the_move
		self.round_over = game.get_round_reward(
			*(self.fd.getCharacter(p).getHp() for p in (self.player, not self.player)),
			self.fd.getRemainingFramesNumber()
		)
		self.parent = parent
		self.mcts = mcts
		self.input_vector = input_vector

		self.edges = {}

		self.P = None
		self.N = 0
		self.valid_mask = None

		# self.input_vector = self.mcts.input_builder.build(self.state)
		# self.id = hash(self.input_vector.to_bytes())

	def __str__(self):
		return self._str(settings.STR_REP_DEPTH)

	def _str(self, depth):
		if depth <= 1:
			return str(self.N)
		return str(self.N) + " -> " + str([a + " -> " + e.child._str(depth - 1) for (a, e) in self.edges.items()])

	def add_child(self, action, new_fd, new_input_vector=None):
		child = Node(new_fd, not self.player, self, self.mcts, new_input_vector)
		self.edges[action] = Edge(self, child)
		return child

	def is_root(self):
		return self.parent is None

	def is_leaf(self):
		return len(self.edges) == 0

	def visited(self):
		return self.P is not None

	def search(self):
		if self.mcts.time_expired():
			return 0

		# print("M2", time.perf_counter(), flush=True)
		# Terminal node
		if self.round_over:
			return self.round_over

		# print("M3", time.perf_counter(), flush=True)
		# Unvisited node
		if not self.visited():
			# print("M4", time.perf_counter(), flush=True)
			return self.visit()

		return self.expand()

	def visit(self):
		# print("M5", time.perf_counter(), flush=True)
		if self.input_vector is None:
			assert settings.NN == 'DataNN'
			self.input_vector = self.mcts.input_builder.build(self.fd)
		# print("M6", time.perf_counter(), flush=True)
		self.P, v = self.mcts.nn.predict(self.input_vector)
		# print("M7", time.perf_counter(), flush=True)
		self.valid_mask = game.valid_moves_mask(self.fd, self.player)
		# print("M8", time.perf_counter(), flush=True)
		self.P *= self.valid_mask
		# print("M9", time.perf_counter(), flush=True)
		sumP = np.sum(self.P)
		if sumP == 0.:
			# print("All valid moves were masked.")
			self.P = self.valid_mask / np.sum(self.valid_mask)
		else:
			self.P /= np.sum(self.P)
		# print("M10", time.perf_counter(), flush=True)
		return -v

	def expand(self):
		# Pick action with the highest UCB
		best_a, best_u, best_e = None, float('-inf'), None
		for i, action in enumerate(settings.ALL_MOVES):
			if self.valid_mask[i]:
				edge = self.edges.get(action)
				if edge:
					u = edge.Q + settings.CPUCT * self.P[i] * math.sqrt(self.N) / (1 + edge.N)
				else:
					u = settings.CPUCT * self.P[i] * math.sqrt(self.N + settings.EPS)
				if u > best_u:
					best_a, best_u, best_e = action, u, edge
		assert best_a is not None

		# print("M11", time.perf_counter(), flush=True)
		self.mcts.action_deque.clear()
		# print("M12", time.perf_counter(), flush=True)
		self.mcts.action_deque.add(self.mcts.enumerated_actions[best_a])
		# print("M13", time.perf_counter(), flush=True)
		next_fd = self.mcts.sim.simulate(self.fd, self.player, self.mcts.action_deque, None, settings.STEP_FRAMES)
		# print("M14", time.perf_counter(), flush=True)
		next_input_v = None
		if settings.NN == 'ImageNN':
			next_input_v = self.mcts.screen_simulate(self.input_vector, self.fd, next_fd)
		# print("M15", time.perf_counter(), flush=True)

		child = self.add_child(best_a, next_fd, next_input_v) if best_a not in self.edges else self.edges[best_a].child
		v = child.search()

		e = self.edges[best_a]
		if best_e:
			assert best_e is e
			e.Q = (e.N * e.Q + v) / (e.N + 1)
			e.N += 1
		else:
			assert e.child is child
			e.Q = v
			e.N = 1

		self.N += 1
		return -v


class Edge(object):
	def __init__(self, in_node, out_node):
		self.parent = in_node
		self.child = out_node

		self.N = 0
		self.Q = 0
