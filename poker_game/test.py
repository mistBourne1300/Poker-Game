from players import *
import utils
import pickle
import numpy as np
p1auth = "1234567890"
p1 = human("steve",p1auth)
p1.new_hand(p1auth, [(0,0),(0,0)])
# print(p1.reveal_hand(p1auth))
# p2auth = 987654321
# p2 = random("STEVE WILL DIE",p2auth)
# p3 = raiser("WINNER HERE", p2)

l = [(9,0,0), (1,0,0), (8,4,1), None, None]
newl = []
for val in l:
    if val is None:
        newl.append((0,0,0))
    else:
        newl.append(val)
newl = np.array(newl)
print(np.argsort(newl,axis=0)[::-1])
print(l)
print(newl)