from players import *
import utils
import pickle
p1auth = "1234567890"
p1 = human("steve",p1auth)
p1.new_hand(p1auth, [(0,0),(0,0)])
print(p1.reveal_hand(p1auth))
# p2auth = 987654321
# p2 = random("STEVE WILL DIE",p2auth)
# p3 = raiser("WINNER HERE", p2)

print()
print(sum([True, True, True, False]))