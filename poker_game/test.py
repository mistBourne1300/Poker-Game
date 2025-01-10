# from players import *
import utils
import pickle
from tqdm import tqdm
import numpy as np
from itertools import permutations
import time


if __name__ == "__main__":
    hand = [utils.str_to_tuple(cstr) for cstr in ['2c','qh']]
    tabled = [utils.str_to_tuple(cstr) for cstr in ['qd', '2s', '7h', 'kd', '7s']]
    num_opps = 2
    np.set_printoptions(suppress=True)
    start = time.time()
    probs = utils.calc_probs_multiple_opps(hand, tabled, num_opps)
    print(probs)
    print(utils.calc_best_hand(hand+tabled))
    print(f"{time.time() - start:.3f} sec")
