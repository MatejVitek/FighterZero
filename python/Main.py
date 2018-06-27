import sys
import os
import argparse

import Settings
from LearnAI import LearnAI
from PlayAI import PlayAI
from py4j.java_gateway import JavaGateway, GatewayParameters as GParams, CallbackServerParameters as CSParams


def main():
	process_command_line_options()
	run_game()
	close_gateway()


def process_command_line_options():
	Settings.AI = [PlayAI, PlayAI]

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
		Settings.GAME_NUM = args.number
	if args.character1:
		Settings.CHARS[0] = args.character1
	if args.character2:
		Settings.CHARS[1] = args.character2

	if args.learn:
		for i in (0, 1):
			Settings.AI[i] = LearnAI
			Settings.INI_FILES[i] = None
			Settings.SAVE_FILE = Settings.DEF_NN_FILE
	else:
		if args.ai1:
			Settings.AI[0] = resolve_import_name(args.ai1)
			Settings.INI_FILES[0] = None
			Settings.SAVE_FILES[0] = Settings.DEF_NN_FILE
		if args.ai2:
			Settings.AI[1] = resolve_import_name(args.ai2)
			Settings.INI_FILES[1] = None
			Settings.SAVE_FILES[1] = Settings.DEF_NN_FILE

	if args.file:
		for i in (0, 1):
			Settings.INI_FILES[i] = args.file
		Settings.SAVE_FILE = args.file
	else:
		if args.file1:
			Settings.INI_FILES[0] = Settings.SAVE_FILES[0] = args.file1
		if args.file2:
			Settings.INI_FILES[1] = Settings.SAVE_FILES[1] = args.file2

	if args.save:
		Settings.SAVE_FILE = args.save
	if args.save1:
		Settings.SAVE_FILES[0] = args.save1
	if args.save2:
		Settings.SAVE_FILES[1] = args.save2


def resolve_import_name(name):
	import importlib
	m, c = name.split('.') if '.' in name else (name, name)
	return getattr(importlib.import_module(m), c)


def run_game():
	os.chdir(".\\networks\\")

	temp_save = [False, False]
	for i in (0, 1):
		if Settings.AI[i] == LearnAI and Settings.SAVE_FILES[i] is None:
			temp_save[i] = True
			Settings.SAVE_FILES[i] = Settings.SAVE_FILE[::-1].replace(".", ".%d_" % (i+1), 1)[::-1]
		Settings.PLAYER = i
		manager.registerAI(Settings.AI[i].__name__, Settings.AI[i](gateway))

	game = manager.createGame(*Settings.CHARS, *(ai.__name__ for ai in Settings.AI), Settings.GAME_NUM)
	print("Game starting")
	manager.runGame(game)

	if all(ai == LearnAI for ai in Settings.AI) and Settings.SAVE_FILE is not None:
		save_better_network(Settings.SAVE_FILE, *(f for f in Settings.SAVE_FILES))
	for i in (0, 1):
		if temp_save[i]:
			os.remove(Settings.SAVE_FILES[i])

	print("Game ending")
	sys.stdout.flush()


def save_better_network(save, nn1, nn2):
	pass


def close_gateway():
	gateway.close_callback_server()
	gateway.close()


if __name__ == '__main__':
	gateway = JavaGateway(gateway_parameters=GParams(port=4242), callback_server_parameters=CSParams())
	manager = gateway.entry_point
	main()
