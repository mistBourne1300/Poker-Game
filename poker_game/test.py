# from players import *
import utils
import pickle
from tqdm import tqdm
import numpy as np
from itertools import permutations


if __name__ == "__main__":
    hand = [utils.str_to_tuple(cstr) for cstr in ['2c','qh']]
    tabled = [utils.str_to_tuple(cstr) for cstr in ['qd', '2s', '7h', 'ks']]
    num_opps = 2

    print(utils.calc_probs_multiple_opps(hand, tabled, num_opps))