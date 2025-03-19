import numpy as np
import time
from heapq import nlargest
import os
import multiprocessing as mp
from tqdm import tqdm
from itertools import combinations
from my_queue import MyQueue
MININTERVAL = 1.0

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
            r = high-i
            if r==1:
                r=14
            rank = strranks[r]
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
            r = high-i
            if r==1:
                r=14
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

def add_to_list(lizt, str_remaining=None, remaining_cards=None, max_size=52):
    if str_remaining is None or remaining_cards is None:
        str_remaining = [r+s for r in strranks for s in strsuits]
        remaining_cards = [(r,s) for r in ranks for s in suits]
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

def computer_add(lizt:list, str_remaining:list=full_str_deck, remaining_cards:list=full_tuple_deck, max_size=52):
    while len(lizt) < max_size:
        next_card_idx = np.random.choice([i for i in range(len(remaining_cards))])
        next_card = remaining_cards.pop(next_card_idx)
        str_remaining.pop(next_card_idx)
        lizt.append(next_card)



def say(msg,printout=True):
    if printout: print(msg)
    exit_code = os.system(f'say "{msg}"')
    if exit_code > 0:
        raise KeyboardInterrupt("interrupt in utils.say()")

def confirm(statement):
    print("confirm " + statement)
    p = mp.Process(target=say, args = ("confirm " + statement,False))
    p.start()
    temp = input("press enter:")
    p.kill()
    p.join()
    p.close()

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
    if num_opps==0 and len(tabled)==5:
        # table is full and number of opponents to calculate is 0. 
        # Simply return the naive probabilities with the self hand probability 1-hot encoded

        self_hand_probs = np.zeros(10)

        selfhand = hand + tabled
        selfres = calc_best_hand(selfhand)

        self_hand_probs[selfres[0]] = 1

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
        opp_hand_probs = [prob_high, prob_pair, prob_two_pair, prob_three_kind, prob_straight, prob_flush, prob_full_house, prob_four_kind, prob_straight_flush, prob_royal_flush]

        prob_matrix = np.zeros((10,10))
        for i,self_prob in enumerate(self_hand_probs):
            for ii,opp_prob in enumerate(opp_hand_probs):
                prob_matrix[i,ii] = self_prob*opp_prob
        
        tie_prob = np.sum(np.diag(prob_matrix))
        win_prob = np.sum(np.tril(prob_matrix)) - tie_prob
        loss_prob = np.sum(np.triu(prob_matrix)) - tie_prob
        wl_probs = np.array([win_prob,loss_prob,tie_prob])

        return self_hand_probs,opp_hand_probs,wl_probs



    # create the deck of cards
    deck, _, _, _, _ = create_deck()
    # remove cards that ar already in hand (2 cards)
    for c in hand:
        deck.remove(c)
    # remove cards that ar already on table (up to 5 cards)
    for c in tabled:
        deck.remove(c)
    # get cpu count
    cpus = mp.cpu_count()

    # create process list and Queue object
    processes = []
    q = MyQueue()
    lock = mp.Lock()
    # we have an incomplete table, so those combos will be the basis for the multiprocessing
    if len(tabled) < 5:
        # create possible future cards that can be laid on table
        num_tabled_remaining = 5-len(tabled)
        future_table = [list(c) for c in tqdm(combinations(deck, num_tabled_remaining), desc="creating combos", leave=False)]
        # get the chunk size, which is how many combinations each cpu will handle
        chunk_size = len(future_table)//cpus
        print(f" starting {cpus} processes...")
        for offset,i in enumerate(range(0,len(future_table), chunk_size)):
            dummy_deck = deck.copy()
            p = mp.Process(target=mp_self_hand_calc, args=(hand, tabled, future_table[i:i+chunk_size],dummy_deck,num_opps,q,offset,lock))
            p.start()
            processes.append(p)
    else:
        # the table is full, we need to call the first recursive call directly
        
        selfhand = hand + tabled
        selfres = calc_best_hand(selfhand)
        first_opp_hands = list(combinations(deck,2))
        chunk_size = len(first_opp_hands)//cpus
        print(f"starting {cpus} processes...")
        for offset,i in enumerate(range(0,len(first_opp_hands), chunk_size)):
            dummy_deck = deck.copy()
            p = mp.Process(target=mp_opp_hand_calc, args=(selfres, tabled, first_opp_hands[i:i+chunk_size], dummy_deck, num_opps, q, offset, lock))
            p.start()
            processes.append(p)



    
    # if we have no opponents, we will simply get our personal hand tallies
    # otherwise, the final recursive call handles the win/loss logic and returns
    # a 0 for a win, 1 for a loss, and 2 for a tie
    # if num_opps == 0:
    #     tally = np.zeros(10)
    # else:
    #     tally = np.zeros(3)


    # create three tallies
    # one to hold self hand information
    # one to hold the opp hand information
    # one to hold the win/loss tally information
    self_tally = np.zeros(10)
    opp_tally = np.zeros(10)
    wl_tally = np.zeros(3)
    
    # double check all processes are finished
    for p in processes:
        p.join()

    
    # empty the queue
    while not q.empty():
        st, ot, wlt = q.get()
        self_tally += st
        opp_tally += ot
        wl_tally += wlt
    
    for p in processes:
        p.close()
    
    # get probabilities from tally
    self_hand_probs = self_tally/np.sum(self_tally)
    opp_hand_probs = opp_tally
    wl_probs = wl_tally
    if num_opps != 0:
        opp_hand_probs = opp_hand_probs/np.sum(opp_tally)
        wl_probs = wl_probs/np.sum(wl_tally)

    else:
        # we don't have a win/loss tally, we have a hand tally
        # the following calculations aren't exactly accurate, 
        # but the probabilities don't change all that much, 
        # so it should be fairly close
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
        opp_hand_probs = [prob_high, prob_pair, prob_two_pair, prob_three_kind, prob_straight, prob_flush, prob_full_house, prob_four_kind, prob_straight_flush, prob_royal_flush]

        prob_matrix = np.zeros((10,10))
        for i,self_prob in enumerate(self_hand_probs):
            for ii,opp_prob in enumerate(opp_hand_probs):
                prob_matrix[i,ii] = self_prob*opp_prob
        
        tie_prob = np.sum(np.diag(prob_matrix))
        win_prob = np.sum(np.tril(prob_matrix)) - tie_prob
        loss_prob = np.sum(np.triu(prob_matrix)) - tie_prob
        wl_probs = np.array([win_prob,loss_prob,tie_prob])

    print()
    return self_hand_probs,opp_hand_probs,wl_probs


def mp_self_hand_calc(hand:list, tabled:list, future_table:list, deck:list, num_opps:list, q:mp.Queue,  offset:int, lock):
    # start tqdm progress bar
    lock.acquire()
    pbar = tqdm(total=len(future_table), desc=f"chunk {offset}", position=offset, mininterval=MININTERVAL,leave=False)
    lock.release()
    start = time.time()
    old = 0

    self_tally = np.zeros(10)
    opp_tally = np.zeros(10)
    wl_tally = np.zeros(3)


    for i,c in enumerate(future_table):
        # progress bar logic
        if time.time() - start > MININTERVAL:
            lock.acquire()
            pbar.update(i-old)
            lock.release()
            old=i
            start = time.time()
        
        # the full cards on the table
        full_tabled = tabled + c

        # cards we personally have access to (2 in hand + 5 on table)
        selfhand = hand + full_tabled
        # get our personal result, which is passed down the recursive levels so we can compare it to the opps results
        selfres = calc_best_hand(selfhand)
        self_tally[selfres[0]] += 1
        if num_opps > 0:
            # we have opponent hands to calculate

            # remove cards from deck
            for card in c:
                deck.remove(card)
            # begin recursively calculating opponent hands
            ot, wlt = recurse_opp_hand_calc(selfres, full_tabled, [], deck, num_opps, pbar=pbar, lock=lock)
            opp_tally += ot
            wl_tally += wlt

            # add cards back into deck
            for card in c:
                deck.append(card)

    # close tqdm bar
    lock.acquire()
    pbar.close()
    lock.release()
    q.put((self_tally,opp_tally,wl_tally))

def mp_opp_hand_calc(selfres:tuple, tabled:list, first_opp_hands:list, deck:list, num_opps:int, q:mp.Queue, offset:int, lock):
    lock.acquire()
    pbar = tqdm(total=len(first_opp_hands), desc=f"chunk {offset}", position=offset, mininterval=MININTERVAL, leave=False)
    lock.release()
    start = time.time()
    old = 0

    self_tally = np.zeros(10)
    self_tally[selfres[0]] = 1
    opp_tally = np.zeros(10)
    wl_tally = np.zeros(3)

    opp_reses = []

    for i,c in enumerate(first_opp_hands):
        # progress bar logic
        if time.time() - start > MININTERVAL:
            lock.acquire()
            pbar.update(i-old)
            lock.release()
            old=i
            start = time.time()
        
        opphand = tabled+list(c)
        oppres = calc_best_hand(opphand)
        opp_tally[oppres[0]] += 1
        if num_opps == 1:
            if selfres > oppres:
                wl_tally[0] += 1
            elif oppres > selfres:
                wl_tally[1] += 1
            else:
                wl_tally[2] += 1
        else:
            opp_reses.append(oppres)
            for card in c:
                deck.remove(card)
            
            ot,wlt = recurse_opp_hand_calc(selfres=selfres, full_tabled=tabled, opp_reses=opp_reses, deck=deck, num_opps=num_opps, pbar=pbar, lock=lock)
            opp_tally += ot
            wl_tally += wlt

            for card in c:
                deck.append(card)
            opp_reses.pop()
    lock.acquire()
    pbar.close()
    lock.release()
    q.put((self_tally,opp_tally,wl_tally))
    

def recurse_opp_hand_calc(selfres:tuple, full_tabled:list, opp_reses:list, deck:list, num_opps:int, pbar=None, lock=None):

    combos = list(combinations(deck,2))

    start = time.time()

    opp_tally = np.zeros(10)
    wl_tally = np.zeros(3)


    for i,c in enumerate(combos): # get all combinations of 2 cards from the remaining deck

        if pbar is not None and lock is not None and time.time() - start > MININTERVAL:
            lock.acquire()
            pbar.set_description(f"{i}/{len(combos)}")
            lock.release()
            start = time.time()

        # get the opp hand and oppres
        opphand = full_tabled + list(c)
        oppres = calc_best_hand(opphand)
        
        # append oppres to the list of opponent results
        opp_reses.append(oppres)
        opp_tally[oppres[0]] += 1
        # print(len(opp_reses))
        if len(opp_reses) == num_opps:
            # we have reached the bottom of the recursion, we need to calculate a win/loss tally and push that onto the queue
            # a returned 0 indicates a win, a returned 1 is a loss, and a 2 is a tie
            # this is so that we can have a win/loss tally marker monitoring the queue, and just have it add one to the respective bucket

            # get the best opponent
            opp_winner = max(opp_reses)

            if selfres > opp_winner: # we beat the best opponent
                wl_tally[0] += 1
            elif selfres < opp_winner: # we lose to the best opponent
                wl_tally[1] += 1
            else: # we tied the best opponent
                wl_tally[2] += 1
        else:
            # remove used cards from deck
            for card in c:
                deck.remove(card)
            
            # go down another level of recursion to get the next opponent's hand
            ot,wlt = recurse_opp_hand_calc(selfres=selfres, full_tabled=full_tabled, opp_reses=opp_reses, deck=deck, num_opps=num_opps)
            opp_tally += ot
            wl_tally += wlt

            # add cards back into deck
            for card in c:
                deck.append(card)
        opp_reses.pop()
    return opp_tally, wl_tally

