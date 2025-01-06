import numpy as np
import time
from heapq import nlargest
import os

ranks = [r for r in range(14,1,-1)]
suits = [s for s in range(4)]
strranks = ['2','3','4','5','6','7','8','9','10','j','q','k','a']
strsuits = ['s','h','c','d']
num_to_hand = ["high card","pair","two pair", "three kind","straight","flush","full house","four kind","straight flush","royal flush"]
remaining_cards = [(r,s) for r in ranks for s in suits]
str_remaining = [r+s for r in strranks for s in strsuits]
full_str_deck = [r+s for r in strranks for s in strsuits]
full_tuple_deck = [(r,s) for r in ranks for s in suits]
strranks = ["0","0"] + strranks
hand = []

def create_deck():
    ranks = [r for r in range(14,1,-1)]
    suits = [s for s in range(4)]
    strranks = ['2','3','4','5','6','7','8','9','10','j','q','k','a']
    strsuits = ['s','h','c','d']
    num_to_hand = ["high card","pair","two pair", "three kind","straight","flush","full house","four kind","straight flush","royal flush"]
    deck = [(r,s) for r in ranks for s in suits]
    strdeck = [r+s for r in strranks for s in strsuits]
    return deck, strdeck, ['0','0'] + strranks, strsuits, num_to_hand


def calc_best_hand(hand):
    scount = np.zeros(4)
    for c in hand:
        scount[c[1]] += 1
    
    # check flush
    flush_bool = scount >= 5
    # fancy_out(flush_bool)
    if np.any(flush_bool):
        # we have a flush
        idx = np.argmax(flush_bool)
        rcount = np.zeros(15)
        for c in hand:
            if c[1] == idx: rcount[c[0]] += 1
        # print(flush)
        # print(rcount)
        high = contains_straight(rcount)

        # print(high)
        if high == 0:
            return 5, *tuple(np.argsort(rcount)[-1:-6:-1]) # flush
        if high == 14: return 9,0,0,0,0,0 # (royal) straight flush
        return 8,high,0,0,0,0 # straight flush
    else:
        # no flush
        rcount = np.zeros(15,dtype=int)
        for c in hand:
            rcount[c[0]] += 1
        
        count_vals = highest_kinds(rcount)
        # if count_vals [0,0] > 4:
        #     raise ValueError(f"count returned higher than 4: {count_vals[0,0]}")
        if count_vals[0,0] == 4:
            if len(count_vals) > 1:
                maximum = max(count_vals[1:,1])
                return 7,count_vals[0,1],maximum,0,0,0 # four kind
            else: return 7,count_vals[0,1],0,0,0,0 # incomplete four kind
        if count_vals[0,0] > 2:
            if len(count_vals) > 1:
                if count_vals[1,0] > 1: return 6,count_vals[0,1],count_vals[1,1],0,0,0 # full house
            high = contains_straight(rcount)
            if high > 0: return 4,high,0,0,0,0 # straight
            if len(count_vals) > 2:
                [maximum, submax] = nlargest(2,count_vals[1:,1])
                return 3,count_vals[0][1],maximum,submax,0,0 # three kind
            elif len(count_vals) == 2:
                print("here")
                maximum = max(count_vals[1:,1])
                print(maximum)
                return 3,count_vals[0,1],maximum,0,0,0 # incomplete three kind
            else:
                return 3,count_vals[0,1],0,0,0,0 # incomplete three kind
        high = contains_straight(rcount)
        if high > 0: return 4,high,0,0,0,0 # straight
        if len(count_vals) > 1:
            if count_vals[1,0] == 2:
                if len(count_vals) > 2:
                    maximum = max(count_vals[2:,1])
                    return 2,count_vals[0,1],count_vals[1,1],maximum,0,0 # two pair
                else:
                    return 2,count_vals[0,1],count_vals[1,1],0,0,0 # incomplete two pair
        if count_vals[0,0] == 2:
            if len(count_vals) > 3:
                [maximum,submax,subsub] = nlargest(3,count_vals[1:,1])
                return 1,count_vals[0,1],maximum,submax,subsub,0 # pair
            elif len(count_vals) > 2:
                [maximum,submax] = nlargest(2,count_vals[1:,1])
                return 1,count_vals[0,1],maximum,submax,0,0 # incomplete pair
            elif len(count_vals) > 1:
                maximum = max(count_vals[1:,1])
                return 1,count_vals[0,1],maximum,0,0,0 # incomplete pair
            else:
                return 1,count_vals[0,1],0,0,0,0
        high_cards = nlargest(5,count_vals[:,1])
        return 0,*high_cards
    
def contains_straight(rcount):
    for high in range(len(rcount)-1,5,-1):
        # print(high)
        finished = True
        for run in range(high,high-5,-1):
            # print(" ",run)
            # print(" ",rcount[run])
            if rcount[run] == 0:
                finished = False
                break
        if finished: return high
    return 0

def highest_kinds(rcount):
    argmaxxes = np.argsort(rcount,kind='stable')[::-1]
    return np.array([(rcount[argmaxxes[i]], argmaxxes[i]) for i in range(5) if rcount[argmaxxes[i]] > 0])

def str_to_tuple(cardstr):
    rank,suit = strranks.index(cardstr[:-1]), strsuits.index(cardstr[-1])
    return (rank, suit)

def tuple_to_str(cardtup):
    return strranks[cardtup[0]] + strsuits[cardtup[1]]

def hand_to_str(hand):
    nruter = "[ "
    for card in hand:
        nruter += tuple_to_str(card) + " "
    nruter += "]"
    return nruter

def fancy_out(msg:str,end="\n", sleep_time = None):
    if sleep_time is None:
        sleep_time = .1/len(msg)
    for c in msg:
        print(c,end="",flush=True)
        time.sleep(sleep_time)
    print("",end=end)

def interpret_hand(best_hand, hand):
    nruter = ""

    def get_flush_suit_str():
        scount = np.zeros(4)
        for c in hand:
            scount[c[1]] += 1
        return strsuits[np.argmax(scount)]


    if best_hand[0] == 9:
        # royal flush
        suit = get_flush_suit_str()
        for r in ['a','k','q','j','10']:
            nruter = nruter + r+suit + " "
        nruter = nruter[:-1]
        pass
    elif best_hand[0] == 8:
        # straight flush
        suit = get_flush_suit_str()
        high = best_hand[1]
        for i in range(5):
            rank = strranks[high-i]
            nruter += rank+suit + " "
        nruter = nruter[:-1]
        pass
    elif best_hand[0] == 7:
        # four kind
        four_rank = strranks[best_hand[1]]
        extra_rank = best_hand[2]
        for suit in strsuits:
            nruter += four_rank+suit + " "
        for c in hand:
            if c[0]==extra_rank:
                nruter += tuple_to_str(c)
                break
        pass
    elif best_hand[0] == 6:
        # full house
        three_rank = best_hand[1]
        two_rank = best_hand[2]
        count = 0
        for c in hand:
            if c[0] == three_rank:
                nruter += tuple_to_str(c) + " "
                count += 1
            if count == 3:
                break
        for c in hand:
            if c[0] == two_rank:
                nruter += tuple_to_str(c) + " "
                count += 1
            if count == 5:
                break
        nruter = nruter[:-1] 
        pass
    elif best_hand[0] == 5:
        # flush
        suit = get_flush_suit_str()
        for r in best_hand[1:]:
            rank = strranks[r]
            nruter = nruter + rank+suit + " "
        nruter = nruter[:-1]
        pass
    elif best_hand[0] == 4:
        # straight
        high = best_hand[1]
        for i in range(5):
            r = high-i
            for c in hand:
                if c[0] == r:
                    nruter = nruter + tuple_to_str(c) + " "
                    break
        nruter = nruter[:-1]
        pass
    elif best_hand[0] == 3:
        # three kind
        three_rank = best_hand[1]
        r1 = best_hand[2]
        r2 = best_hand[3]
        count = 0
        for c in hand:
            if c[0] == three_rank:
                nruter = nruter + tuple_to_str(c) + " "
                count += 1
            if count == 3:
                break
        for c in hand:
            if c[0] == r1:
                nruter = nruter + tuple_to_str(c) + " "
                break
        for c in hand:
            if c[0] == r2:
                nruter = nruter + tuple_to_str(c)
                break
        pass
    elif best_hand[0] == 2:
        # two pair
        prank1 = best_hand[1]
        prank2 = best_hand[2]
        extra_rank = best_hand[3]
        count = 0
        for c in hand:
            if c[0] == prank1:
                nruter = nruter + tuple_to_str(c) + " "
                count += 1
            if count == 2:
                break
        for c in hand:
            if c[0] == prank2:
                nruter = nruter + tuple_to_str(c) + " "
                count += 1
            if count == 4:
                break
        for c in hand:
            if c[0] == extra_rank:
                nruter = nruter + tuple_to_str(c)
                break
        pass
    elif best_hand[0] == 1:
        # pair
        prank = best_hand[1]
        extra1 = best_hand[2]
        extra2 = best_hand[3]
        extra3 = best_hand[4]
        count = 0
        for c in hand:
            if c[0] == prank:
                nruter = nruter + tuple_to_str(c) + " "
                count += 1
            if count == 2:
                break
        for r in [extra1,extra2,extra3]:
            for c in hand:
                if c[0] == r:
                    nruter = nruter + tuple_to_str(c) + " "
                    break
        nruter = nruter[:-1]
        pass
    else:
        # high card
        for r in best_hand[1:]:
            for c in hand:
                if c[0] == r:
                    nruter = nruter + tuple_to_str(c) + " "
                    break
        nruter = nruter[:-1]
        pass
    return nruter

def add_to_hand():
        next_cards = input("enter next cards: ")
        any_added = False
        for next_card in next_cards.split():
            if len(next_card) == 2 and next_card[0] == "1":
                next_card = next_card[0] + "0" + next_card[1]
            if next_card not in str_remaining:
                print(f"{next_card} is not a valid card. skipping")
            else:
                any_added = True
                str_remaining.remove(next_card)
                card = str_to_tuple(next_card)
                remaining_cards.remove(card)
                hand.append(card)
        return any_added

def add_to_list(lizt, str_remaining=full_str_deck, remaining_cards=full_tuple_deck, max_size=52):
    next_cards = input("enter next cards: ")
    any_added = False
    for next_card in next_cards.split():
        if len(lizt) >= max_size:
            print("lizt maximum size reached, breaking")
            break
        if len(next_card) == 2 and next_card[0] == "1":
            next_card = next_card[0] + "0" + next_card[1]
        if next_card not in str_remaining:
            print(f"{next_card} is not a valid card. skipping")
        else:
            any_added = True
            str_remaining.remove(next_card)
            card = str_to_tuple(next_card)
            try:
                remaining_cards.remove(card)
            except Exception as e:
                print(next_card)
                print(card)
                print(remaining_cards)
                raise e
            lizt.append(card)
    return any_added

def say(msg):
    print(msg)
    os.system(f'say "{msg}"')

def confirm(statement):
    print("confirm " + statement)
    os.system(f'say "confirm {statement}"')
    temp = input("press enter:")