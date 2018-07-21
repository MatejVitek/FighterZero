import sys
import os
import subprocess
import argparse

import settings
from settings import P
from LearnAI import LearnAI
from PlayAI import PlayAI
from py4j.java_gateway import JavaGateway, GatewayParameters as GParams, CallbackServerParameters as CSParams


JAVA_CMD = 'javaw -Dfile.encoding=UTF-8' \
           ' -classpath .\\bin;' \
           '.\\jar\\FightingICE.jar;' \
           '.\\lib\\lwjgl\\lwjgl_util.jar;' \
           '.\\lib\\lwjgl\\lwjgl-glfw.jar;' \
           '.\\lib\\lwjgl\\lwjgl-openal.jar;' \
           '.\\lib\\lwjgl\\lwjgl-opengl.jar;' \
           '.\\lib\\lwjgl\\lwjgl.jar;' \
           '.\\lib\\natives\\windows\\lwjgl-glfw-natives-windows.jar;' \
           '.\\lib\\natives\\windows\\lwjgl-natives-windows.jar;' \
           '.\\lib\\natives\\windows\\lwjgl-openal-natives-windows.jar;' \
           '.\\lib\\natives\\windows\\lwjgl-opengl-natives-windows.jar;' \
           '.\\lib\\javax.json-1.0.4.jar;' \
           '.\\lib\\py4j0.10.4.jar' \
           ' Main --py4j'


def main():
	if len(sys.argv) > 1:
		process_command_line_options()
	if wait_for_server():
		settings.JVM = gateway.jvm
		run_game()


def start_java_server():
	print("Starting Java server...")
	os.chdir('..\\')
	return subprocess.Popen(JAVA_CMD + settings.JAVA_ARGS, stdout=subprocess.PIPE, universal_newlines=True)


def wait_for_server():
	print("Waiting for Java server to finish initialisation...")
	while True:
		line = server.stdout.readline().strip()
		if server.poll() is not None and line == '':
			return False
		if line == 'INIT_DONE':
			return True
		print(line)


def process_command_line_options():
	ap = argparse.ArgumentParser(description="Start a game of FGAI.")
	ap.add_argument('-n', '--number', help="number of games to play")
	ap.add_argument('-c1', '--character1', help="character for P1")
	ap.add_argument('-c2', '--character2', help="character for P2")
	ap.add_argument('-l', '--learn', action='store_true', help="use LearnAI for both players")
	ap.add_argument('-p', '--play', action='store_true', help="use LearnAI for both players")
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
		settings.GAME_NUM = args.number
	if args.character1:
		settings.CHARS[P[0]] = args.character1
	if args.character2:
		settings.CHARS[P[1]] = args.character2

	if args.learn:
		for p in P:
			settings.AI[p] = LearnAI
			settings.INI_FILES[p] = None
			settings.SAVE_FILES[p] = None
			settings.SAVE_FILE = settings.DEF_NN_FILE
	elif args.play:
		for p in P:
			settings.AI[p] = PlayAI
			settings.INI_FILES[p] = settings.DEF_NN_FILE
			settings.SAVE_FILES[p] = None
			settings.SAVE_FILE = None
	else:
		if args.ai1:
			settings.AI[P[0]] = args.ai1
			settings.INI_FILES[P[0]] = None
			settings.SAVE_FILES[P[0]] = settings.DEF_NN_FILE
			settings.SAVE_FILE = None
		if args.ai2:
			settings.AI[P[1]] = args.ai2
			settings.INI_FILES[P[1]] = None
			settings.SAVE_FILES[P[1]] = settings.DEF_NN_FILE
			settings.SAVE_FILE = None

	if args.file:
		for p in P:
			settings.INI_FILES[p] = args.file
		settings.SAVE_FILE = args.file
	else:
		if args.file1:
			settings.INI_FILES[P[0]] = settings.SAVE_FILES[P[0]] = args.file1
		if args.file2:
			settings.INI_FILES[P[1]] = settings.SAVE_FILES[P[1]] = args.file2

	if args.save:
		settings.SAVE_FILE = args.save
	if args.save1:
		settings.SAVE_FILES[P[0]] = args.save1
	if args.save2:
		settings.SAVE_FILES[P[1]] = args.save2


def run_game():
	print("Setting up game...")

	temp_save = {P[0]: False, P[1]: False}
	for p in P:
		if isinstance(settings.AI[p], str):
			settings.AI[p] = resolve_import_name(settings.AI[p])
		if settings.AI[p] == LearnAI and settings.SAVE_FILES[p] is None:
			temp_save[p] = True
			settings.SAVE_FILES[p] = settings.SAVE_FILE[::-1].replace('.', f".{1 if p else 2}P_", 1)[::-1]
		if settings.AI[p] in (LearnAI, PlayAI):
			manager.registerAI(settings.AI[p].__name__, settings.AI[p]())
		else:
			manager.registerAI(settings.AI[p].__name__, settings.AI[p](gateway))

	chars, ais = zip(*((settings.CHARS[p], settings.AI[p].__name__) for p in P))
	game = manager.createGame(*chars, *ais, settings.GAME_NUM)
	print("Game starting...")
	manager.runGame(game)

	if all(settings.AI[p] == LearnAI for p in P) and settings.SAVE_FILE is not None:
		save_better_network(settings.SAVE_FILE, *(settings.SAVE_FILES[p] for p in P))
	for p in P:
		if temp_save[p]:
			os.remove(settings.SAVE_FILES[p])

	print("Game ending.")
	sys.stdout.flush()


def resolve_import_name(name):
	import importlib
	m, c = name.split('.') if '.' in name else (name, name)
	return getattr(importlib.import_module(m), c)


def save_better_network(save, nn1, nn2):
	pass


def close_gateway():
	gateway.close_callback_server()
	gateway.close()


def close_server():
	server.kill()


if __name__ == '__main__':
	server = start_java_server()
	gateway = JavaGateway(gateway_parameters=GParams(port=settings.PORT), callback_server_parameters=CSParams())
	manager = gateway.entry_point
	try:
		main()
	finally:
		close_gateway()
		close_server()
