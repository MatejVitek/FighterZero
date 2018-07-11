# Game constants
P = PLAYERS = True, False
C = ALL_CHARS = 'ZEN', 'GARNET', 'LUD'
GROUND_MOVES = (None, 'STAND_D_DB_BA', 'BACK_STEP', 'FORWARD_WALK', 'DASH', 'JUMP', 'FOR_JUMP', 'BACK_JUMP',
                'STAND_GUARD', 'CROUCH_GUARD', 'THROW_A', 'THROW_B', 'STAND_A', 'STAND_B', 'CROUCH_A', 'CROUCH_B',
                'STAND_FA', 'STAND_FB', 'CROUCH_FA', 'CROUCH_FB', 'STAND_D_DF_FA', 'STAND_D_DF_FB', 'STAND_F_D_DFA',
                'STAND_F_D_DFB', 'STAND_D_DB_BB', 'STAND_D_DF_FC')
AIR_MOVES = (None, 'AIR_GUARD', 'AIR_A', 'AIR_B', 'AIR_DA', 'AIR_DB', 'AIR_FA', 'AIR_FB', 'AIR_UA', 'AIR_UB',
             'AIR_D_DF_FA', 'AIR_D_DF_FB', 'AIR_F_D_DFA', 'AIR_F_D_DFB', 'AIR_D_DB_BA', 'AIR_D_DB_BB')
ROUNDS = 3
ROUND_TIME = 60
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

# Game settings
# "RND" for full random, random.choice(C) for initial random
CHARS = {P[0]: 'ZEN', P[1]: 'ZEN'}
GAME_NUM = 2
HP = {P[0]: 400, P[1]: 400}


# AI Constants
DEF_NN_FILE = "MyNN.h5"

# AI Settings
AI = {P[0]: 'LearnAI', P[1]: 'LearnAI'}
INI_FILES = {P[0]: None, P[1]: None}
SAVE_FILES = {P[0]: None, P[1]: None}
SAVE_FILE = DEF_NN_FILE


# NN Constants
DEF_SIZE = 1
FD_SIZE = 2
CD_SIZE = 70
AD_SIZE = 24
MAX_PROJ = 3
INPUT_SIZE = DEF_SIZE + FD_SIZE + 2 * CD_SIZE + (2 * MAX_PROJ + 1) * AD_SIZE

# NN Settings
HIDDEN_LAYERS = 4


# Java constants
JVM = None
ARG_LIMIT_HP = f' --limithp {HP[P[0]]} {HP[P[1]]}'
ARG_MUTE = ' --mute'
ARG_FAST = ' --fastmode'
ARG_BLACK = ' --black-bg'
ARG_GREY = ' --grey-bg'
ARG_INVERT1 = ' --inverted-player 1'
ARG_INVERT2 = ' --inverted-player 2'
ARG_TRAINING = ' -t'

ARGS_PLAY = ARG_LIMIT_HP + ARG_MUTE
ARGS_LEARN = ARG_LIMIT_HP + ARG_FAST
ARGS_COMPETITION = ARG_LIMIT_HP + ARG_GREY + ARG_INVERT1

# Java settings
JAVA_ARGS = ARGS_PLAY
PORT = 4242
