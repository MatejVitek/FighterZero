import time
import math
import numpy as np

import game
import settings


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

	def search(self, initial_state, initial_input_vector, player, temp=1.):
		self.root = Node(initial_state, player, None, self, initial_input_vector)
		self.start = time.perf_counter()
		while not self.time_expired():
			print("M1", time.perf_counter(), flush=True)
			self.root.search()

		N = np.array([self.root.edges[action].N if action in self.root.edges else 0 for action in settings.ALL_MOVES])
		N = N.astype(float)

		if all(x == 0. for x in N):
			print("All probabilities are 0.")
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

	def __str__(self):
		return str(self.root)


class Node(object):
	def __init__(self, state, player_on_the_move, parent, mcts, input_vector=None):
		self.state = state
		self.player = player_on_the_move
		self.round_over = game.get_round_reward(
			*(self.state.getCharacter(p).getHp() for p in (self.player, not self.player)),
			self.state.getRemainingFramesNumber()
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

	def add_child(self, action, new_state):
		child = Node(new_state, not self.player, self, self.mcts)
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

		print("M2", time.perf_counter(), flush=True)
		# Terminal node
		if self.round_over:
			return self.round_over

		print("M3", time.perf_counter(), flush=True)
		# Unvisited node
		if not self.visited():
			print("M4", time.perf_counter(), flush=True)
			return self.visit()

		return self.expand()

	def visit(self):
		print("M5", time.perf_counter(), flush=True)
		if self.input_vector is None:
			self.input_vector = self.mcts.input_builder.build(self.state)
		print("M6", time.perf_counter(), flush=True)
		self.P, v = self.mcts.nn.fast_predict(self.input_vector)
		print("M7", time.perf_counter(), flush=True)
		self.valid_mask = game.valid_moves_mask(self.state, self.player)
		print("M8", time.perf_counter(), flush=True)
		self.P = self.P * self.valid_mask
		print("M9", time.perf_counter(), flush=True)
		try:
			self.P /= np.sum(self.P)
		except ZeroDivisionError:
			print("All valid moves were masked.")
			self.P = self.valid_mask / np.sum(self.valid_mask)
		print("M10", time.perf_counter(), flush=True)
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

		print("M11", time.perf_counter(), flush=True)
		self.mcts.action_deque.clear()
		print("M12", time.perf_counter(), flush=True)
		self.mcts.action_deque.add(self.mcts.enumerated_actions[best_a])
		print("M13", time.perf_counter(), flush=True)
		next_state = self.mcts.sim.simulate(self.state, self.player, self.mcts.action_deque, None, settings.STEP_FRAMES)
		print("M14", time.perf_counter(), flush=True)

		child = self.add_child(best_a, next_state) if best_a not in self.edges else self.edges[best_a].child
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
