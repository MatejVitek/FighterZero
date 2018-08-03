import numpy as np


# Game constants
P = PLAYERS = True, False
C = ALL_CHARS = 'ZEN', 'GARNET', 'LUD'
GROUND_MOVES = (
    'STAND_D_DB_BA', 'BACK_STEP', 'FORWARD_WALK', 'DASH', 'JUMP', 'FOR_JUMP', 'BACK_JUMP', 'STAND_GUARD',
    'CROUCH_GUARD', 'THROW_A', 'THROW_B', 'STAND_A', 'STAND_B', 'CROUCH_A', 'CROUCH_B', 'STAND_FA', 'STAND_FB',
    'CROUCH_FA', 'CROUCH_FB', 'STAND_D_DF_FA', 'STAND_D_DF_FB', 'STAND_F_D_DFA', 'STAND_F_D_DFB', 'STAND_D_DB_BB',
    'STAND_D_DF_FC'
)
AIR_MOVES = (
    'AIR_GUARD', 'AIR_A', 'AIR_B', 'AIR_DA', 'AIR_DB', 'AIR_FA', 'AIR_FB', 'AIR_UA', 'AIR_UB', 'AIR_D_DF_FA',
    'AIR_D_DF_FB', 'AIR_F_D_DFA', 'AIR_F_D_DFB', 'AIR_D_DB_BA', 'AIR_D_DB_BB'
)
VALID_MOVES = {
    'GROUND': np.concatenate([np.ones(len(GROUND_MOVES)), np.zeros(len(AIR_MOVES)), np.ones(1)]),
    'AIR': np.concatenate([np.zeros(len(GROUND_MOVES)), np.ones(len(AIR_MOVES) + 1)])
}
ALL_MOVES = GROUND_MOVES + AIR_MOVES + ('NEUTRAL',)

FPS = 60
COMBO_LIMIT = 30
MAX_SPEEDX = 35
MAX_SPEEDY = 30
ATT_MAX_FRAMES = 90
ATT_MAX_COST = -300
ATT_MAX_ENERGY = 60
ATT_MAX_GUARD_REC = 30
ATT_MAX_DMG = 300
ATT_MAX_IMPACT = 30
STAGE_WIDTH = 960
STAGE_HEIGHT = 640


# Game settings
# 'RND' for full random, random.choice(C) for initial random
CHARS = {P[0]: 'ZEN', P[1]: 'ZEN'}
GAME_NUM = 9
ROUNDS = 3
ROUND_TIME = 30
LIMIT_HP = True
HP = {P[0]: 400, P[1]: 400}


# NN Constants
# DataNN
DEF_SIZE = 1
FD_SIZE = 2
CD_SIZE = 70
AD_SIZE = 25
MAX_PROJ = 3
# INPUT_SIZE = DEF_SIZE + FD_SIZE + 2 * CD_SIZE + (1 + 2 * MAX_PROJ) * AD_SIZE  # OLD SIZE
INPUT_SIZE = 8

# NN Settings
NN = 'ImageNN'
REG_CONST = 1e-4
DROPOUT_RATE = 0  # If 0, dropout layers won't be used. (old value: 0.1)
LEARNING_RATE = .1
MOMENTUM = .9
# DataNN
HIDDEN_LAYERS = 2
# ImageNN
IMAGE_WIDTH = STAGE_WIDTH // 10
IMAGE_HEIGHT = STAGE_HEIGHT // 10
CHANNELS = 128
FIRST_FILTER_SIZE = 7
FILTER_SIZE = 3
RES_LAYERS = 2


# AI Constants
DEF_NN_FILE = f"My{NN}.h5"

# AI Settings
AI = {P[0]: 'LearnAI', P[1]: 'LearnAI'}
INI_FILES = {P[0]: DEF_NN_FILE, P[1]: DEF_NN_FILE}
SAVE_FILES = {P[0]: DEF_NN_FILE, P[1]: DEF_NN_FILE}


# MCTS & Learning Constants
EPS = 1e-6

# MCTS & Learning Settings
TIME_LIMIT = 5 * (1 / FPS - 1e-3)
CPUCT = 1.
TEMP = 2.
STEP_FRAMES = 15
STR_REP_DEPTH = 2
ROUND_REWARD_WEIGHT = .8
EPOCHS = 10
BATCH_SIZE = 32


# Java constants
JVM = None
ARG_HP = lambda: f' --limithp {HP[P[0]]} {HP[P[1]]}' if LIMIT_HP else ''
ARG_MUTE = ' --mute'
ARG_FAST = ' --fastmode'
ARG_BLACK = ' --black-bg'
ARG_GREY = ' --grey-bg'
ARG_INVERT1 = ' --inverted-player 1'
ARG_INVERT2 = ' --inverted-player 2'
ARG_TRAINING = ' -t'
ARG_TIME = lambda: f' --time {ROUND_TIME}'
ARG_ROUNDS = lambda: f' -r {ROUNDS}'

ARGS_PLAY = lambda: ARG_HP() + ARG_MUTE
ARGS_LEARN = lambda: ARG_HP() + ARG_FAST  # Don't use with screenData-reliant methods
ARGS_COMPETITION = lambda: ARG_HP() + ARG_GREY + ARG_INVERT1 + ARG_MUTE
ARGS_ROUND_SETTINGS = lambda: ARG_TIME() + ARG_ROUNDS()

# Java settings
JAVA_ARGS = lambda: ARGS_COMPETITION() + ARGS_ROUND_SETTINGS()
PORT = 4242


