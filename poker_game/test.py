from players import *
import utils
import pickle
from tqdm import tqdm
import numpy as np
from itertools import permutations

actual = (5,11,10,9,8,6)

for perm in tqdm(list(permutations(['9d', '6d', '8d', '10d', 'jd', '3d', '2d']))):
    # print(perm)
    hand = [utils.str_to_tuple(rs) for rs in perm]
    best_hand_tuple = utils.calc_best_hand(hand)
    if best_hand_tuple != actual:
        print(perm)
        print(best_hand_tuple)
        print()
    

    

print("best hand tuple:",utils.calc_best_hand(hand))
