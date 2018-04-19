import sys
from py4j.java_gateway import JavaGateway, GatewayParameters as GParams, CallbackServerParameters as CSParams
from KickAI import KickAI
from machete import Machete


ALL_CHARS = "ZEN", "GARNET", "LUD"

# Game settings
# "RND" for full random, random.choice(ALL_CHARS) for initial random
CHARS = "RND", "RND"
GAME_NUM = 2
AI1 = KickAI
AI2 = Machete


def main():
    start_game()
    close_gateway()


def start_game():
    p1 = AI1(gateway)
    p2 = AI2(gateway)
    manager.registerAI(AI1.__name__, p1)
    manager.registerAI(AI2.__name__, p2)

    print("Start game")
    game = manager.createGame(*CHARS, AI1.__name__, AI2.__name__, GAME_NUM)
    manager.runGame(game)

    print("After game")
    sys.stdout.flush()


def close_gateway():
    gateway.close_callback_server()
    gateway.close()


gateway = JavaGateway(gateway_parameters=GParams(port=4242), callback_server_parameters=CSParams())
manager = gateway.entry_point
main()
