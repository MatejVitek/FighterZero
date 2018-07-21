import settings


def get_round_reward(my_hp, opp_hp, frames_left):
	if frames_left > 0 and my_hp > 0 and opp_hp > 0:
		return 0
	return (my_hp - opp_hp) * settings.ROUND_REWARD_CONSTANT


def is_round_over(state):
	return state.getRemainingFramesNumber() <= 0 or any(state.getCharacter(p).getHp() <= 0 for p in settings.P)


def valid_moves_mask(state, player):
	if str(state.getCharacter(player).getState()) == 'AIR':
		return settings.VALID_MOVES['AIR']
	else:
		return settings.VALID_MOVES['GROUND']
