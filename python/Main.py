import sys
import os
import argparse

from LearnAI import LearnAI
from PlayAI import PlayAI
from py4j.java_gateway import JavaGateway, GatewayParameters as GParams, CallbackServerParameters as CSParams

ALL_CHARS = "ZEN", "GARNET", "LUD"
DEF_NN_FILE = 'MyNN.h5'

# Game settings
# "RND" for full random, random.choice(ALL_CHARS) for initial random
GAME_NUM = 2
CHARS = ["ZEN", "ZEN"]
AI = [PlayAI, PlayAI]
INIFILES = [DEF_NN_FILE, DEF_NN_FILE]
SAVEFILES = [None, None]
SAVEFILE = None


def main():
	process_command_line_options()
	print(AI, INIFILES, SAVEFILES, SAVEFILE, sep='\t')
	run_game()
	close_gateway()


def process_command_line_options():
	global GAME_NUM, CHARS, AI, INIFILES, SAVEFILES, SAVEFILE

	ap = argparse.ArgumentParser(description="Start a game of FGAI.")
	ap.add_argument('-n', '--number', help="number of games to play")
	ap.add_argument('-c1', '--character1', help="character for P1")
	ap.add_argument('-c2', '--character2', help="character for P2")
	ap.add_argument('-l', '--learn', action='store_true', help="use LearnAI for both players")
	ap.add_argument('-p1', '-ai1', '--ai1', '-AI1', '--AI1', '--player1', dest='ai1',
	                help="AI to use for P1; can be module.Class or just Class if module and class names are the same")
	ap.add_argument('-p2', '-ai2', '--ai2', '-AI2', '--AI2', '--player2', dest='ai2',
	                help="AI to use for P2; can be module.Class or just Class if module and class names are the same")
	ap.add_argument('-f', '--file', help="initialise both NNs from specified file (for use with default AIs)")
	ap.add_argument('-f1', '--file1', help="initialise NN for P1 from specified file (for use with default AIs)")
	ap.add_argument('-f2', '--file2', help="initialise NN for P2 from specified file (for use with default AIs)")
	ap.add_argument('-s', '--save', help="save better NN to specified file at the end (for use with LearnAI)")
	ap.add_argument('-s1', '--save1', help="save P1's NN to specified file at the end (for use with LearnAI)")
	ap.add_argument('-s2', '--save2', help="save P2's NN to specified file at the end (for use with LearnAI)")

	args = ap.parse_args()

	if args.number:
		GAME_NUM = args.number
	if args.character1:
		CHARS[0] = args.character1
	if args.character2:
		CHARS[1] = args.character2

	if args.learn:
		for i in (0, 1):
			AI[i] = LearnAI
			INIFILES[i] = None
			SAVEFILE = DEF_NN_FILE
	else:
		if args.ai1:
			AI[0] = resolve_import_name(args.ai1)
			INIFILES[0] = None
			SAVEFILES[0] = DEF_NN_FILE
		if args.ai2:
			AI[1] = resolve_import_name(args.ai2)
			INIFILES[1] = None
			SAVEFILES[1] = DEF_NN_FILE

	if args.file:
		for i in (0, 1):
			INIFILES[i] = args.file
		SAVEFILE = args.file
	else:
		if args.file1:
			INIFILES[0] = SAVEFILES[0] = args.file1
		if args.file2:
			INIFILES[1] = SAVEFILES[1] = args.file2

	if args.save:
		SAVEFILE = args.save
	if args.save1:
		SAVEFILES[0] = args.save1
	if args.save2:
		SAVEFILES[1] = args.save2


def resolve_import_name(name):
	import importlib
	m, c = name.split('.') if '.' in name else (name, name)
	return getattr(importlib.import_module(m), c)


def run_game():
	os.chdir(".\\networks\\")

	temp_saves = [None, None]
	for i in (0, 1):
		if AI[i] == LearnAI:
			if SAVEFILES[i] is None:
				temp_saves[i] = SAVEFILE[::-1].replace(".", ".%d_" % (i+1), 1)[::-1]
				p = AI[i](gateway, INIFILES[i], temp_saves[i])
			else:
				p = AI[i](gateway, INIFILES[i], SAVEFILES[i])
		elif AI[i] == PlayAI:
			p = AI[i](gateway, INIFILES[i])
		else:
			p = AI[i](gateway)
		manager.registerAI(AI[i].__name__, p)

	print("Starting game")

	game = manager.createGame(*CHARS, AI[0].__name__, AI[1].__name__, GAME_NUM)
	manager.runGame(game)

	if AI[0] == AI[1] == LearnAI and SAVEFILE is not None:
		nn1 = SAVEFILES[0] if SAVEFILES[0] is not None else temp_saves[0]
		nn2 = SAVEFILES[1] if SAVEFILES[1] is not None else temp_saves[1]
		save_better_network(SAVEFILE, nn1, nn2)
	for i in (0, 1):
		if temp_saves[i] is not None:
			os.remove(temp_saves[i])

	print("Game ending")
	sys.stdout.flush()


def save_better_network(save, nn1, nn2):
	pass


def close_gateway():
	gateway.close_callback_server()
	gateway.close()


gateway = JavaGateway(gateway_parameters=GParams(port=4242), callback_server_parameters=CSParams())
manager = gateway.entry_point

if __name__ == '__main__':
	main()
