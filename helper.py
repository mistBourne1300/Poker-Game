import argparse
import os
import time
import numpy as np
from itertools import combinations
from tqdm.auto import tqdm
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
    This will calculate the probability of various poker hands at each stage of a Texas Hold 'Em hand."
helpstring = f"the valid card arguments are {str_remaining}"
# changes how often progress bars are updated. small numbers are cool-looking, 
# but results in more print locks, (and obviously more prints) that slow down computation
MININTERVAL = 0.5

def display_probs_mp(hand):
    combos = [list(c) for c in tqdm(combinations(remaining_cards,7-len(hand)),desc="generating combos",leave=False)]
    cpus = mp.cpu_count()
    chunk_size = len(combos)//cpus
    processes = []
    q = mp.SimpleQueue()
    lock = mp.Lock()
    print(f" starting {cpus} processes...",end="\r")
    for offset,i in enumerate(range(0,len(combos),chunk_size)):
        # print(i,":",i+chunk_size)
        p = mp.Process(target=calc_buckets_mp, args=(hand,combos[i:i+chunk_size],q,offset,lock))
        p.start()
        processes.append(p)
    
    buckets = np.zeros(10,dtype=int)
    for p in processes:
        p.join()
    while not q.empty():
        small_buckets = q.get()
        buckets += small_buckets
    
    os.system("clear")
    print(f"your hand: {hand_to_str(hand)}")
    # print(f"buckets: {buckets}")
    probs = buckets/np.sum(buckets)
    your_msg = "Your Hand Probabilities"
    terminal_len = os.get_terminal_size()[0]
    bar="-"*terminal_len
    fancy_out(f"{your_msg}")
    fancy_out(f"{bar}")
    for i in range(len(probs)-1,-1,-1):
        fancy_out(f"{num_to_hand[i]:.<16}: = {np.round(probs[i],7)}")


    choose_52_7 = 133784560
    prob_royal_flush = 4324/choose_52_7
    prob_straight_flush = 37260/choose_52_7
    prob_four_kind = 224848/choose_52_7
    prob_full_house = 3473184/choose_52_7
    prob_flush = 4047644/choose_52_7
    prob_straight = 6180020/choose_52_7
    prob_three_kind = 6461620/choose_52_7
    prob_two_pair = 31433400/choose_52_7
    prob_pair = 58627800/choose_52_7
    prob_high = 23294460/choose_52_7
    opp_probs = [prob_high, prob_pair, prob_two_pair, prob_three_kind, prob_straight, prob_flush, prob_full_house, prob_four_kind, prob_straight_flush, prob_royal_flush]

    prob_matrix = np.zeros((10,10))
    for i,self_prob in enumerate(probs):
        for ii,opp_prob in enumerate(opp_probs):
            prob_matrix[i,ii] = self_prob*opp_prob
    
    tie_prob = np.sum(np.diag(prob_matrix))
    win_prob = np.sum(np.tril(prob_matrix)) - tie_prob
    loss_prob = np.sum(np.triu(prob_matrix)) - tie_prob
    probs = np.array([win_prob,loss_prob,tie_prob])


    win_msg = "Win probability:"
    loss_msg = "Loss Probability:"
    tie_msg = "Tie Probability:"
    print()
    fancy_out(f"{win_msg: <20}\u2248 {np.round(probs[0],7)}")
    fancy_out(f"{loss_msg: <20}\u2248 {np.round(probs[1],7)}")
    fancy_out(f"{tie_msg: <20}\u2248 {np.round(probs[2],7)}")
    print()

def calc_buckets_mp(hand,combos,q:mp.SimpleQueue,offset:int, lock):
    """
        here, we assume combos is a list of lists, not a list of tuples
    """
    buckets = np.zeros(10,dtype=int)
    lock.acquire()
    pbar = tqdm(total=len(combos),desc=f"chunk {offset}", position=offset,leave=False)
    lock.release()
    start = time.time()
    old = 0
    for i,c in enumerate(combos):
        if time.time() - start > MININTERVAL:
            lock.acquire()
            pbar.update(i-old)
            lock.release()
            old = i
            start = time.time()
        revealed = hand + c
        buckets[calc_best_hand(revealed)[0]] += 1
    lock.acquire()
    pbar.close()
    lock.release()
    q.put(buckets)

def gen_self_combos(hand):
    num_remaining = 7-len(hand)
    return [list(c) for c in tqdm(combinations(remaining_cards,num_remaining),desc="creating combos",leave=False)]

def gen_opp_combos():
    return [list(c) for c in tqdm(combinations(remaining_cards,2),desc="generating combos",leave=False)]

def display_probs_mp_win_loss(hand):
    assert len(hand) + len(remaining_cards) == 52
    cpus = mp.cpu_count()
    processes = []
    if len(hand) < 7:
        combos = gen_self_combos(hand)
        chunk_size = len(combos)//cpus
        q = mp.SimpleQueue()
        lock = mp.Lock()
        print(f" starting {cpus} processes...",end="\r")
        for offset,i in enumerate(range(0,len(combos), chunk_size)):
            p = mp.Process(target=calc_self_and_opp_buckets_and_win_counter_mp, args=(hand,combos[i:i+chunk_size],q,offset,lock))
            p.start()
            processes.append(p)
    elif len(hand) == 7:
        combos = gen_opp_combos()
        chunk_size = len(combos)//cpus
        q = mp.SimpleQueue()
        print(f" starting {cpus} processes...",end="\r")
        for i in range(0,len(combos),chunk_size):
            p = mp.Process(target=final_calc, args=(hand,combos[i:i+chunk_size],q))
            p.start()
            processes.append(p)
    else:
        raise RuntimeError(f"somehow, hand length became {len(hand)}")

    self_buckets = np.zeros(10)
    opp_buckets = np.zeros(10)
    win_loss_tally = np.zeros(3)
    for p in processes:
        p.join()
    while not q.empty():
        self_partial, opp_partial, win_partial = q.get()
        self_buckets += self_partial
        opp_buckets += opp_partial
        win_loss_tally += win_partial
    self_probs = self_buckets/np.sum(self_buckets)
    opp_probs = opp_buckets/np.sum(opp_buckets)
    win_probs = win_loss_tally/np.sum(win_loss_tally)

    os.system("clear")
    print(f"your hand: {hand_to_str(hand)}")
    # print(f"buckets: {self_buckets}")
    your_msg = "Your Hand Probabilities"
    opp_msg = "Opponent Hand Probabilities"
    terminal_len = os.get_terminal_size()[0]
    bar="-"*terminal_len
    fancy_out(f"{your_msg: <36}{opp_msg}")
    fancy_out(f"{bar}")
    for i in range(len(self_probs)-1,-1,-1):
        fancy_out(f"{num_to_hand[i]:.<16}: = {np.round(self_probs[i],7):<20}{num_to_hand[i]:.<16}: \u2248 {np.round(opp_probs[i],7)}")
    
    win_msg = "Win probability:"
    loss_msg = "Loss Probability:"
    tie_msg = "Tie Probability:"
    print()
    fancy_out(f"{win_msg: <20}\u2248 {np.round(win_probs[0],7)}")
    fancy_out(f"{loss_msg: <20}\u2248 {np.round(win_probs[1],7)}")
    fancy_out(f"{tie_msg: <20}\u2248 {np.round(win_probs[2],7)}")
    print()

def calc_self_and_opp_buckets_and_win_counter_mp(hand,combos,q:mp.SimpleQueue,offset:int,lock):
    """
        accepts a list of lists, eash sublist is a list of tuples that are of the form
        (rank,suit) for ranks 2-14 (inc.) and suits 0-3 (inc.)
        each sublist L will have exactly 7 cards
        we will then generate all combinations of opponent's hands, and use those to 
        calculate the win/loss tallies

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
    dummy_deck = remaining_cards.copy()
    lock.acquire()
    pbar = tqdm(total=len(combos),desc=f"chunk {offset}", position=offset, mininterval=MININTERVAL,leave=False)
    lock.release()
    start = time.time()
    old = 0
    for i,c in enumerate(combos):
        if time.time() - start > MININTERVAL:
            lock.acquire()
            pbar.update(i-old)
            lock.release()
            old = i
            start = time.time()
        for card in c:
            dummy_deck.remove(card)
        selfhand = hand+c
        selfres = calc_best_hand(selfhand)
        self_buckets[selfres[0]] += 1
        # print("hand:",hand+c)
        for o in combinations(dummy_deck,2):
            ophand = selfhand[2:] + list(o)
            oppres = calc_best_hand(ophand)
        
            opp_buckets[oppres[0]] += 1

            if selfres > oppres:
                win_loss_tally[0] += 1
            elif selfres < oppres:
                win_loss_tally[1] += 1
            else:
                win_loss_tally[2] += 1
        
        for card in c:
            dummy_deck.append(card)
    pbar.close()
    q.put((self_buckets, opp_buckets, win_loss_tally))

def final_calc(hand,combos,q:mp.SimpleQueue):
    """
        this is very similar to the main method below, but it assumes hand is a complete collection of 7 cards
        and that combos is the generated opponent cards (list of list of 2 cards each)
    """
    self_buckets = np.zeros(10)
    opp_buckets = np.zeros(10)
    win_loss_tally = np.zeros(3)
    selfres = calc_best_hand(hand)
    self_buckets[selfres[0]] += 1
    for i,c in enumerate(combos):
        ophand = hand[2:]+c
        oppres = calc_best_hand(ophand)
        opp_buckets[oppres[0]] += 1

        if selfres > oppres:
            win_loss_tally[0] += 1
        elif selfres < oppres:
            win_loss_tally[1] += 1
        else:
            win_loss_tally[2] += 1
    # pbar.close()
    q.put((self_buckets, opp_buckets, win_loss_tally))

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
                maximum = max(count_vals[1:,1])
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
    for high in range(len(rcount)-1,4,-1):
        # print(high)
        finished = True
        for run in range(high,high-5,-1):
            # print(" ",run)
            # print(" ",rcount[run])
            if rcount[run] == 0:
                finished = False
                break
        if finished: return high
    if rcount[5] and rcount[4] and rcount[3] and rcount[2] and rcount[14]:
        return 5
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
            r = high-i
            if r==1:
                r=14
            rank = strranks[r]
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
            if r==1:
                r=14
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

def main(args,unknown):
    hand = []
    os.system("clear")
    for next_card in [c for c in args.cards] + [c for c in unknown]:
        if len(next_card) == 2 and next_card[0] == "1":
            print(next_card+" triggered special 10")
            next_card = next_card[0] + "0" + next_card[1]
            print(next_card)
            time.sleep(3)
        if next_card not in str_remaining:
            print(f'skipping: {next_card} is not a valid card. run with flag --help or -h to see valid card strings.')
        else:
            str_remaining.remove(next_card)
            card = str_to_tuple(next_card)
            remaining_cards.remove(card)
            hand.append(card)
    

    def add_to_hand():
        next_cards = input("enter next cards: ")
        any_added = False
        for next_card in next_cards.split():
            if len(hand) >= 7:
                break
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
    
    terminated = False
    while not terminated:
        try:
            os.system("clear")
            fancy_out(f"your hand: {hand_to_str(hand)}")
            if len(hand) == 2:
                display_probs_mp(hand)
            elif len(hand) > 4:
                display_probs_mp_win_loss(hand)
            if len(hand) > 1:
                best_hand = calc_best_hand(hand)
                fancy_out(f"\nyour best hand: {num_to_hand[best_hand[0]]}")
                fancy_out(str(np.array(best_hand,dtype=int))+ " -> " +interpret_hand(best_hand,hand))
            if len(hand) >= 7:
                break
                
            
            while not add_to_hand():
                print(f"no cards added. valid cards:\n{str_remaining}")
            
        except KeyboardInterrupt as e:
            try:
                os.system("clear")
                fancy_out("ctrl-c detected. press enter to undo card add")
                fancy_out("enter 'a' to add cards without recalculation")
                fancy_out("press ctrl-c again to terminate")
                i = input()
                if len(hand) > 0:
                    remaining_cards.append(hand[-1])
                    str_remaining.append(tuple_to_str(hand[-1]))
                    hand = hand[:-1]
                if i == 'a':
                    fancy_out(f"your hand: {hand_to_str(hand)}")
                    while not add_to_hand():
                        print(f"no cards added. valid cards:\n{str_remaining}")
            except KeyboardInterrupt as e2:
                os.system("clear")
                terminated = True

            
    fancy_out("process terminated",sleep_time=.03)

        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Poker Trick Helper",
        description=prog_desc
    )
    parser.add_argument("-c",'--cards',nargs='+',help=helpstring,default=[])
    args,unknown = parser.parse_known_args()
    main(args,unknown)