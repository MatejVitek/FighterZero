import sys
import argparse

from LearnAI import LearnAI
from PlayAI import PlayAI
from py4j.java_gateway import JavaGateway, GatewayParameters as GParams, CallbackServerParameters as CSParams

ALL_CHARS = "ZEN", "GARNET", "LUD"

# Game settings
# "RND" for full random, random.choice(ALL_CHARS) for initial random
CHARS = "ZEN", "ZEN"
GAME_NUM = 2
AI1 = PlayAI
AI2 = PlayAI
FILE1 = FILE2 = 'MyAI.nn'


def main():
	start_game()
	close_gateway()


def process_command_line_options():
	global AI1, AI2, FILE1, FILE2

	ap = argparse.ArgumentParser(description="Start a game of FGAI with the specified AI players.")
	ap.add_argument('-l', '--learn', action='store_true', help="use LearnAI for both players")
	ap.add_argument('-f', '--file', help="initialise networks from specified file (for use with default AIs)")
	ap.add_argument('-p1', '-ai1', '--ai1', '-AI1', '--AI1', '--player1', nargs=2, dest='ai1',
					help="AI to use for P1; can be module.Class or just Class if module and class names are the same")
	ap.add_argument('-p2', '-ai2', '--ai2', '-AI2', '--AI2', '--player2', nargs=2, dest='ai2',
					help="AI to use for P2; can be module.Class or just Class if module and class names are the same")
	ap.add_argument('-f1', '--file1', help="initialise network for P1 from specified file (for use with default AIs)")
	ap.add_argument('-f2', '--file2', help="initialise network for P2 from specified file (for use with default AIs)")

	args = ap.parse_args()

	if args.learn:
		AI1 = LearnAI
		AI2 = LearnAI
		FILE1 = None
		FILE2 = None
	else:
		if args.ai1:
			AI1 = resolve_import_name(args.ai1)
		if args.ai2:
			AI2 = resolve_import_name(args.ai2)
	if args.file:
		FILE1 = args.file
		FILE2 = args.file
	else:
		if args.file1:
			FILE1 = args.file1
		if args.file2:
			FILE2 = args.file2


def resolve_import_name(name):
	import importlib
	m, c = name.split('.') if '.' in name else name, name
	return getattr(importlib.import_module(m), c)


def start_game():
	p1 = AI1(gateway)
	p2 = AI2(gateway)
	manager.registerAI(AI1.__name__, p1)
	manager.registerAI(AI2.__name__, p2)

	print("Starting game")
	game = manager.createGame(*CHARS, AI1.__name__, AI2.__name__, GAME_NUM)
	manager.runGame(game)

	print("Game ending")
	sys.stdout.flush()


def close_gateway():
	gateway.close_callback_server()
	gateway.close()


gateway = JavaGateway(gateway_parameters=GParams(port=4242), callback_server_parameters=CSParams())
manager = gateway.entry_point

if __name__ == '__main__':
	process_command_line_options()

main()
