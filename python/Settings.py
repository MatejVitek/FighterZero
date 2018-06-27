ALL_CHARS = "ZEN", "GARNET", "LUD"
DEF_NN_FILE = 'MyNN.h5'

AIR_MOVES =    [None, 'AIR_GUARD', 'AIR_A', 'AIR_B', 'AIR_DA', 'AIR_DB', 'AIR_FA', 'AIR_FB', 'AIR_UA', 'AIR_UB',
                'AIR_D_DF_FA', 'AIR_D_DF_FB', 'AIR_F_D_DFA', 'AIR_F_D_DFB', 'AIR_D_DB_BA', 'AIR_D_DB_BB']

GROUND MOVES = [None, 'STAND_D_DB_BA', 'BACK_STEP', 'FORWARD_WALK', 'DASH', 'JUMP', 'FOR_JUMP', 'BACK_JUMP',
                'STAND_GUARD', 'CROUCH_GUARD', 'THROW_A', 'THROW_B', 'STAND_A', 'STAND_B', 'CROUCH_A', 'CROUCH_B',
                'STAND_FA', 'STAND_FB', 'CROUCH_FA', 'CROUCH_FB', 'STAND_D_DF_FA', 'STAND_D_DF_FB', 'STAND_F_D_DFA',
                'STAND_F_D_DFB', 'STAND_D_DB_BB', 'STAND_D_DF_FC']

# Game settings
# "RND" for full random, random.choice(ALL_CHARS) for initial random
CHARS = ["ZEN", "ZEN"]
GAME_NUM = 2

# NN settings


# Other stuff
AI = [None, None]
INI_FILES = [DEF_NN_FILE, DEF_NN_FILE]
SAVE_FILES = [None, None]
SAVE_FILE = None
PLAYER = 0
