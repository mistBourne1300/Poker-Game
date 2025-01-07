import numpy as np
import time
from heapq import nlargest
import os
import multiprocessing as mp
from tqdm import tqdm
from itertools import combinations
from my_queue import MyQueue
MININTERVAL = 0.5

ranks = [r for r in range(14,1,-1)]
suits = [s for s in range(4)]
strranks = ['2','3','4','5','6','7','8','9','10','j','q','k','a']
strsuits = ['s','h','c','d']
num_to_hand = ["high card","pair","two pair", "three kind","straight","flush","full house","four kind","straight flush","royal flush"]
# remaining_cards = [(r,s) for r in ranks for s in suits]
# str_remaining = [r+s for r in strranks for s in strsuits]
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
        rcount = np.zeros(15,dtype=int)
        for c in hand:
            if c[1] == idx: rcount[c[0]] += 1
        # print("rcount:",rcount)
        # print("argssorted:",np.argsort(rcount)[::-1][:5])
        high = contains_straight(rcount)

        # print(high)
        if high == 0:
            return 5, *tuple(np.argsort(rcount,kind='stable')[-1:-6:-1]) # flush
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
    nruter = []
    for card in hand:
        nruter.append(tuple_to_str(card))
    return str(nruter)

def fancy_out(msg:str,end="\n", sleep_time = None):
    if sleep_time is None:
        sleep_time = .1/len(msg)
    for c in msg:
        print(c,end="",flush=True)
        time.sleep(sleep_time)
    print("",end=end)

def interpret_hand(best_hand, hand):
    nruter = []

    def get_flush_suit_str():
        scount = np.zeros(4)
        for c in hand:
            scount[c[1]] += 1
        return strsuits[np.argmax(scount)]


    if best_hand[0] == 9:
        # royal flush
        suit = get_flush_suit_str()
        for r in ['a','k','q','j','10']:
            nruter.append(r+suit)
        pass
    elif best_hand[0] == 8:
        # straight flush
        suit = get_flush_suit_str()
        high = best_hand[1]
        for i in range(5):
            rank = strranks[high-i]
            nruter.append(rank+suit)
        pass
    elif best_hand[0] == 7:
        # four kind
        four_rank = strranks[best_hand[1]]
        extra_rank = best_hand[2]
        for suit in strsuits:
            nruter.append(four_rank+suit)
        for c in hand:
            if c[0]==extra_rank:
                nruter.append(tuple_to_str(c))
                break
        pass
    elif best_hand[0] == 6:
        # full house
        three_rank = best_hand[1]
        two_rank = best_hand[2]
        count = 0
        for c in hand:
            if c[0] == three_rank:
                nruter.append(tuple_to_str(c))
                count += 1
            if count == 3:
                break
        for c in hand:
            if c[0] == two_rank:
                nruter.append(tuple_to_str(c))
                count += 1
            if count == 5:
                break
        pass
    elif best_hand[0] == 5:
        # flush
        suit = get_flush_suit_str()
        for r in best_hand[1:]:
            rank = strranks[r]
            nruter.append(rank+suit)
        pass
    elif best_hand[0] == 4:
        # straight
        high = best_hand[1]
        for i in range(5):
            r = high-i
            for c in hand:
                if c[0] == r:
                    nruter.append(tuple_to_str(c))
                    break
        pass
    elif best_hand[0] == 3:
        # three kind
        three_rank = best_hand[1]
        r1 = best_hand[2]
        r2 = best_hand[3]
        count = 0
        for c in hand:
            if c[0] == three_rank:
                nruter.append(tuple_to_str(c))
                count += 1
            if count == 3:
                break
        for c in hand:
            if c[0] == r1:
                nruter.append(tuple_to_str(c))
                break
        for c in hand:
            if c[0] == r2:
                nruter.append(tuple_to_str(c))
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
                nruter.append(tuple_to_str(c))
                count += 1
            if count == 2:
                break
        for c in hand:
            if c[0] == prank2:
                nruter.append(tuple_to_str(c))
                count += 1
            if count == 4:
                break
        for c in hand:
            if c[0] == extra_rank:
                nruter.append(tuple_to_str(c))
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
                nruter.append(tuple_to_str(c))
                count += 1
            if count == 2:
                break
        for r in [extra1,extra2,extra3]:
            for c in hand:
                if c[0] == r:
                    nruter.append(tuple_to_str(c))
                    break
        pass
    elif best_hand[1] == 0:
        # folded
        pass
    else:
        # high card
        for r in best_hand[1:]:
            for c in hand:
                if c[0] == r:
                    nruter.append(tuple_to_str(c))
                    break
        pass
    return nruter

def add_to_hand(str_remaining=full_str_deck, remaining_cards=full_tuple_deck):
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

def card_list_to_card_names(cards):
    nruter = []
    for card in cards:
        r = card[0]
        cardname = ""
        if r == 'a':
            cardname = "ace of "
        elif r == 'k':
            cardname = "king of "
        elif r == 'q':
            cardname = "queen of "
        elif r == 'j':
            cardname = "jack of "
        elif r == '1':
            cardname = "10 of "
        elif r == '9':
            cardname = "9 of "
        elif r == '8':
            cardname = "8 of "
        elif r == '7':
            cardname = "7 of "
        elif r == '6':
            cardname = "6 of "
        elif r == '5':
            cardname = "5 of "
        elif r == '4':
            cardname = "4 of "
        elif r == '3':
            cardname = "3 of "
        elif r == '2':
            cardname = "2 of "
        
        s = card[-1]
        if s == 's':
            cardname += "spades"
        elif s == 'h':
            cardname += "hearts"
        elif s == 'c':
            cardname += "clubs"
        elif s == 'd':
            cardname += "diamonds"
        nruter.append(cardname)
    return nruter


def calc_probs_multiple_opps(hand:list, tabled:list, num_opps:int):
    deck, _, _, _, _ = create_deck()
    for c in hand:
        deck.remove(c)
    for c in tabled:
        deck.remove(c)
    cpus = mp.cpu_count()
    processes = []
    win_loss_tally = np.zeros(3)
    q = MyQueue()
    if len(tabled) < 5:
        num_tabled_remaining = 5-len(tabled)
        future_table = [list(c) for c in tqdm(combinations(deck, num_tabled_remaining), desc="creating combos", leave=False)]
        chunk_size = len(future_table)//cpus
        lock = mp.Lock()
        print(f" starting {cpus} processes...")
        for offset,i in enumerate(range(0,len(future_table), chunk_size)):
            p = mp.Process(target=mp_self_hand_calc, args=(hand, tabled, future_table[i:i+chunk_size],deck,num_opps,q,offset,lock))
            p.start()
            processes.append(p)
    else:
        pass
    
    win_loss_tally = np.zeros(3)
    def processes_going(processes=processes):
        for p in processes:
            if p.is_alive():
                return True
        return False
    
    while processes_going():
        while q.qsize() > 100:
            win_loss_tally[q.get()] += 1
    
    for p in processes:
        p.join()
    
    while not q.empty():
        win_loss_tally[q.get()] += 1
    print()
    win_loss_probs = win_loss_tally/np.sum(win_loss_tally)
    return win_loss_probs

def mp_self_hand_calc(hand:list, tabled:list, future_table:list, deck:list, num_opps:list, q:mp.Queue,  offset:int, lock):
    dummy_deck = deck.copy()
    lock.acquire()
    pbar = tqdm(total=len(future_table), desc=f"chunk {offset}", position=offset, mininterval=MININTERVAL,leave=False)
    lock.release()
    start = time.time()
    old = 0
    for i,c in enumerate(future_table):
        if time.time() - start > MININTERVAL:
            lock.acquire()
            pbar.update(i-old)
            lock.release()
            old=i
            start = time.time()
        for card in c:
            dummy_deck.remove(card)
        full_tabled = tabled + c
        selfhand = hand + full_tabled
        selfres = calc_best_hand(selfhand)
        recurse_opp_hand_calc(selfres, full_tabled, [], dummy_deck, num_opps, q)

        for card in c:
            dummy_deck.append(card)
    lock.acquire()
    pbar.close()
    lock.release()

def recurse_opp_hand_calc(selfres:tuple, full_tabled:list, opp_reses:list, deck:list, num_opps:int, q:mp.Queue):
    

    for c in combinations(deck,2):
        opphand = full_tabled + list(c)
        oppres = calc_best_hand(opphand)
        opp_reses.append(oppres)
        # print(len(opp_reses))
        if len(opp_reses) == num_opps:
            # we have reached the bottom of the recursion, we need to calculate a win/loss tally and push that onto the queue
            # a returned 0 indicates a win, a returned 1 is a loss, and a 2 is a tie
            # this is so that we can have a win/loss tally marker monitoring the queue, and just have it add one to the respective bucket
            opp_winner = max(opp_reses)
            if selfres > opp_winner:
                q.put(0)
            elif selfres < opp_winner:
                q.put(1)
            else:
                q.put(2)
            opp_reses.pop()
        else:
            dummy_deck = deck.copy()
            # we need to 
            for card in c:
                dummy_deck.remove(card)
            
            recurse_opp_hand_calc(selfres, full_tabled, opp_reses, dummy_deck, num_opps, q)

            for card in c:
                dummy_deck.append(card)

