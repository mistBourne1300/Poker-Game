import argparse
import os
import time
import numpy as np
from scipy.special import comb
from scipy.stats import binom
from itertools import combinations, product
from tqdm.auto import tqdm
import sys
import multiprocessing as mp
from heapq import nlargest

# TODO: make a best possible hand method
# TODO: refactor all probability calculations, 
# either by fixing the mutual exclusivity problem (which won't allow for best possible hand predictions)
# or by using some other method, that takes into account the (future) best possible hand calculations

ranks = [r for r in range(14,1,-1)]
suits = [s for s in range(4)]
remaining_cards = [(r,s) for r in ranks for s in suits]
strranks = ['2','3','4','5','6','7','8','9','10','j','q','k','a']
strsuits = ['s','h','c','d']
str_remaining = [r+s for r in strranks for s in strsuits]
strranks = ['0','0']+strranks
num_to_hand = ["high card","pair","two pair", "three kind","straight","flush","full house","four kind","straight flush","royal flush"]
prog_desc = "This is a probability calculator for poker hands. \
    This (eventually) will calculate the probability of various poker hands at each stage of a Texas Hold 'Em hand."
helpstring = f"the valid card arguments are {str_remaining}"

def calc_self_and_opp_buckets_and_win_counter_mp(combos,q:mp.SimpleQueue):
    """
        accepts a list of lists, eash sublist is a list of tuples that are of the form
        (rank,suit) for ranks 2-14 (inc.) and suits 0-3 (inc.)
        each sublist L will have exactly 9 cards
        and is broken down as such:
            L[-2:]  = the opponent's hand
            L[:2]   = your hand
            L[2:-2] = the table cards
        each of L[:-2] (your usable cards) and L[2:] (the opponents usable cards) will be passed into the calc_best_hand function
        and the best hand returned. the opponent's and your tallied buckets wlll be updated, and a winner decided (ties allowed) 
        the win/loss bucket will be a list of [num_wins, num_losses, num_ties]
        we will then put your bucket, the opponent's bucket, and the win/loss bucket into q
        for later retrieval by the parent process

        Parameters:
            combos (list):          a list of lists of tuples (see above), each sublist contains all information
                                        on yours and the opponent's hand, and the cards on the table
            
            q (mp.SimpleQueue):     an mp.SimpleQueue object to facilitate multiprocessing

        Returns:
            self_buckets (list):    the tallies of your winning hands in combos, in the same order as the num_to_hand list defined above

            opp_buckets (list):     the tallies of the opponent's winning hands in combos, same order

            win_loss_tally (list):  the tallies of wins, losses, and ties (from your perspective) in combos             
    """
    self_buckets = np.zeros(10)
    opp_buckets = np.zeros(10)
    win_loss_tally = np.zeros(3)
    for c in combos:
        oppres = calc_best_hand(c[2:])
        selfres = calc_best_hand(c[:-2])
        self_best = selfres[0]
        opp_best = oppres[0]
        self_buckets[self_best] += 1
        opp_buckets[opp_best] += 1
        if selfres > oppres:
            win_loss_tally[0] += 1
        elif selfres < oppres:
            win_loss_tally[1] += 1
        else:
            win_loss_tally[2] += 1
    
    q.put((self_buckets, opp_buckets, win_loss_tally))

def calc_buckets_mp(hand,combos,q:mp.SimpleQueue):
    """
        here, we assume combos is a list of lists, not a list of tuples
    """
    buckets = np.zeros(10)
    for c in combos:
        revealed = hand + c
        buckets[calc_best_hand(revealed)[0]] += 1
    q.put(buckets)

# def calc_buckets(hand):
#     buckets = np.zeros(10)
#     remain_to_turn = 7-len(hand)
#     tot = comb(len(remaining_cards),remain_to_turn)
#     i = 0
#     start_time = time.time()
#     for c in combinations(remaining_cards,r=remain_to_turn):
#         if i%10000 == 0:
#             print(f'  {i}/{tot}  {100*((i+1)/tot):.3f}% eta: {(time.time()-start_time)*((tot-i)/(i+1)):.0f} sec   ',end='\r')
#         i += 1
#         revealed = hand+list(c)
#         buckets[calc_best_hand(revealed)] += 1
        
#     return buckets

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
            return 5, tuple(np.argsort(rcount)[-1:-6:-1]) # flush
        if high == 14: return 9,0,0,0,0,0 # (royal) straight flush
        return 8,high,0,0,0,0 # straight flush
    else:
        # no flush
        rcount = np.zeros(15)
        for c in hand:
            rcount[c[0]] += 1
        
        count_vals = highest_kinds(rcount)
        # if count_vals [0,0] > 4:
        #     raise ValueError(f"count returned higher than 4: {count_vals[0,0]}")
        if count_vals[0,0] == 4:
            maximum = nlargest(1,count_vals[1:,1])
            return 7,count_vals[0,1],maximum,0,0,0 # four kind
        if count_vals[0,0] > 2:
            if count_vals[1,0] > 1: return 6,count_vals[0,1],count_vals[1,1],0,0,0 # full house
            high = contains_straight(rcount)
            if high > 0: return 4,high,0,0,0,0 # straight
            [maximum, submax] = nlargest(2,count_vals[1:,1])
            return 3,count_vals[0][1],maximum,submax,0,0 # three kind
        high = contains_straight(rcount)
        if high > 0: return 4,high,0,0,0,0 # straight
        if count_vals[1,0] == 2:
            maximum = nlargest(1,count_vals[2:,1])
            return 2,count_vals[0,1],count_vals[1,1],maximum,0,0 # two pair
        if count_vals[0,0] == 2:
            [maximum,submax,subsub] = nlargest(3,count_vals[1:,1])
            return 1,count_vals[0,1],maximum,submax,subsub,0 # pair
        high_cards = nlargest(5,count_vals[:,1])
        return 0,high_cards
    
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
    argmaxxes = np.argsort(rcount)[::-1]
    return np.array([(rcount[argmaxxes[i]], argmaxxes[i]) for i in range(5)])# if rcount[argmaxxes[i]] > 0])

def str_to_tuple(cardstr):
    rank,suit = strranks.index(cardstr[:-1]), strsuits.index(cardstr[-1])
    return (rank, suit)

# def display_probs(hand):
#     buckets = calc_buckets(hand)
#     print()
#     probs = buckets/np.sum(buckets)
#     for i in range(len(probs)-1,-1,-1):
#         print(f"{num_to_hand[i]:.<16}: {probs[i]}")

def display_probs_mp(hand):
    combos = [list(c) for c in tqdm(combinations(remaining_cards,7-len(hand)),desc="creating combos", leave=False)]
    cpus = mp.cpu_count()
    chunk_size = len(combos)//cpus
    processes = []
    q = mp.SimpleQueue()
    for i in tqdm(range(0,len(combos),chunk_size),desc="starting processes",leave=False):
        # print(i,":",i+chunk_size)
        p = mp.Process(target=calc_buckets_mp, args=(hand,combos[i:i+chunk_size],q))
        p.start()
        processes.append(p)
    
    buckets = np.zeros(10)
    for p in tqdm(processes,desc="waiting for results",leave=False):
        p.join()
    while not q.empty():
        small_buckets = q.get()
        buckets += small_buckets
    # q.close()
    probs = buckets/np.sum(buckets)
    your_msg = "Your Hand Probabilities"
    terminal_len = os.get_terminal_size()[0]
    bar="-"*terminal_len
    fancy_out(f"{your_msg}")
    fancy_out(f"{bar}")
    for i in range(len(probs)-1,-1,-1):
        fancy_out(f"{num_to_hand[i]:.<16}: {np.round(probs[i],7)}")

def gen_combos(hand):
    num_remaining = 7-len(hand)
    dummy_deck = remaining_cards.copy()
    all_combos = []
    num_created = 0
    # for table in tqdm(combinations(remaining_cards,num_remaining),desc="creating combos", leave=False):
    for table in combinations(remaining_cards,num_remaining):
        for card in table:
            dummy_deck.remove(card)
        for c in combinations(dummy_deck,2):
            num_created += 1
            if num_created % 10000 == 0:
                print(f" creating combos: {num_created}", end="\r")
            all_combos.append(hand+list(table)+list(c))
        for card in table:
            dummy_deck.append(card)
    return all_combos

def display_probs_mp_win_loss(hand):
    assert len(hand) + len(remaining_cards) == 52
    combos = gen_combos(hand) #[hand+list(c) for c in tqdm(combinations(remaining_cards, num_remaining), desc="creating combos", leave=False)]

    cpus = mp.cpu_count()
    chunk_size = len(combos)//cpus
    processes = []
    q = mp.SimpleQueue()
    for i in tqdm(range(0,len(combos), chunk_size), desc="starting processes", leave=False):
        p = mp.Process(target=calc_self_and_opp_buckets_and_win_counter_mp, args=(combos[i:i+chunk_size],q))
        p.start()
        processes.append(p)

    self_buckets = np.zeros(10)
    opp_buckets = np.zeros(10)
    win_loss_tally = np.zeros(3)
    for p in tqdm(processes, desc="waiting for results", leave=False):
        p.join()
    while not q.empty():
        self_partial, opp_partial, win_partial = q.get()
        self_buckets += self_partial
        opp_buckets += opp_partial
        win_loss_tally += win_partial
    fancy_out(f"self buckets: {self_buckets}")
    self_probs = self_buckets/np.sum(self_buckets)
    opp_probs = opp_buckets/np.sum(opp_buckets)
    win_probs = win_loss_tally/np.sum(win_loss_tally)

    your_msg = "Your Hand Probabilities"
    opp_msg = "Opponent Hand Probabilities"
    terminal_len = os.get_terminal_size()[0]
    bar="-"*terminal_len
    fancy_out(f"{your_msg: <36}{opp_msg}")
    fancy_out(f"{bar}")
    for i in range(len(self_probs)-1,-1,-1):
        fancy_out(f"{num_to_hand[i]:.<16}: {np.round(self_probs[i],7):<20}{num_to_hand[i]:.<16}: {np.round(opp_probs[i],7)}")
    
    win_msg = "Win probability:"
    loss_msg = "Loss Probability:"
    tie_msg = "Tie Probability:"
    print()
    fancy_out(f"{win_msg: <20}{np.round(win_probs[0],7)}")
    fancy_out(f"{loss_msg: <20}{np.round(win_probs[1],7)}")
    fancy_out(f"{tie_msg: <20}{np.round(win_probs[2],7)}")
    print()

def fancy_out(msg:str):
    sleep_time = .1/len(msg)
    for c in msg:
        print(c,end="",flush=True)
        time.sleep(sleep_time)
    print()

def main(args,unknown):
    hand = []
    os.system("clear")
    strhand = []
    for next_card in [c for c in args.cards] + [c for c in unknown]:
        if next_card not in str_remaining:
            raise ValueError(f'{next_card} is not a valid card. run with flag --help or -h to see valid card strings.')
        else:
            str_remaining.remove(next_card)
            strhand.append(next_card)
            card = str_to_tuple(next_card)
            remaining_cards.remove(card)
            hand.append(card)
    

    while len(hand)<2:
        fancy_out(f"your hand: {strhand}")
        next_card = input("enter next card: ")
        while next_card not in str_remaining:
            next_card = input(f'{next_card} is not a valid card. valid cards:\n{str_remaining}\nenter next card: ')
        str_remaining.remove(next_card)
        strhand.append(next_card)
        card = str_to_tuple(next_card)
        remaining_cards.remove(card)
        hand.append(card)
    
    while len(hand) < 7:
        os.system("clear")
        fancy_out(f"your hand: {strhand}")
        if len(hand) == 2:
            display_probs_mp(hand)
        elif len(hand) > 4:
            display_probs_mp_win_loss(hand)
            
        
        next_card = input("enter next card: ")
        while next_card not in str_remaining:
            next_card = input(f'{next_card} is not a valid card. valid cards:\n{str_remaining}\nenter next card: ')
        str_remaining.remove(next_card)
        strhand.append(next_card)
        card = str_to_tuple(next_card)
        remaining_cards.remove(card)
        hand.append(card)
    
    os.system("clear")
    fancy_out(f"your hand: {strhand}")
    best_hand = calc_best_hand(hand)
    display_probs_mp_win_loss(hand)
    fancy_out(f"\nyour best hand: {num_to_hand[best_hand[0]]}")
    print(best_hand)

        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Poker Trick Helper",
        description=prog_desc
    )
    parser.add_argument("-c",'--cards',nargs='+',help=helpstring,default=[])
    args,unknown = parser.parse_known_args()
    main(args,unknown)