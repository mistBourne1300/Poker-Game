# from players import *
import utils
import pickle
from tqdm import tqdm
import numpy as np
from itertools import permutations
import time


if __name__ == "__main__":
    hand = [utils.str_to_tuple(cstr) for cstr in ['2c','qh']]
    tabled = [utils.str_to_tuple(cstr) for cstr in ['kh','as','9c','8d']]
    num_opps = 1
    # np.set_printoptions(suppress=True)
    start = time.time()
    probs = utils.calc_probs_multiple_opps(hand, tabled, num_opps)
    for p in probs:
        print(p)
    # print(utils.calc_best_hand(hand+tabled))
    print(f"{time.time() - start:.3f} sec")
