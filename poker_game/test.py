# from players import *
import utils
import pickle
from tqdm import tqdm
import numpy as np
from itertools import permutations


if __name__ == "__main__":
    hand = [utils.str_to_tuple(cstr) for cstr in ['2c','qh']]
    tabled = [utils.str_to_tuple(cstr) for cstr in ['qd', '2s', '7h', 'kd']] # 'qd', '2s', '7h', 'kd' weird stuff here. an ace or a king makes the lose probability to go 1
    num_opps = 1
    np.set_printoptions(suppress=True)
    probs = utils.calc_probs_multiple_opps(hand, tabled, num_opps)
    print(probs)
    print(utils.calc_best_hand(hand+tabled))