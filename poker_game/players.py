import numpy as np
import time
from abc import ABC, abstractmethod
import os
import pickle
import json
import hashlib
import multiprocessing as mp
from math import comb
from itertools import combinations
from tqdm import tqdm

from utils import *

class player:
    """
        A player base class for a poker game. Subclasses should implement the __make_decision() method,
        which actually makes the decision on how much money to bet. 
        The rules of poker will be mostly be enforced by the table class, which will
        hold a list of all players.
        The table class will call the decide() function with all it's parameters.
        decide then calls __make_decision() for the player's bet_amount, performs some cursory checks,
        then returns the amount.
        Additionally, blind() will be called by the table class for both the small and big blinds.
    """
    def __init__(self, name:str, auth):
        self.hand = (None,None)
        self.money = 0
        self.name = name
        self.auth = self.hash_auth(auth)

    @staticmethod
    @abstractmethod
    def constructor(name:str, auth):
        return player(name,auth)

    def hash_auth(self,auth):
        # get the bits of the auth object, and do something with them
        hashable = str(auth).encode()
        sha256 = hashlib.sha256()
        sha256.update(hashable)
        return sha256.hexdigest()

    @abstractmethod
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        bet_amount = call_amount
        if bet_amount > self.money:
            bet_amount = self.money
        return bet_amount
    
    def decide(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        bet_amount = 0
        try:
            bet_amount = self.make_decision(auth=auth, call_amount=call_amount, tabled_cards=tabled_cards, others_worth=others_worth, pot=pot, player_bids=player_bids, player_turn=player_turn, player_names=player_names, folded_players=folded_players)
        except Exception as e:
            import traceback
            print(f"player {self.name} threw an error ({e})! This causes a fold.")
            print(traceback.format_exc())
            bet_amount = 0
        print(f"bet amount: {bet_amount}")
        print(f"self money: {self.money}")
        if bet_amount > self.money:
            print(f"player {self.name} tried to cheat by betting more than they have. They're all in now!")
            bet_amount = self.money
            self.money = 0
        elif 0 < bet_amount < call_amount and bet_amount < self.money:
            print(f"player {self.name} tried to cheat by not going all in! As a consequence, they fold.")
            bet_amount = 0
        else:
            self.money -= bet_amount
        return bet_amount

    def worth(self):
        return self.money
    
    def blind(self, auth, amount):
        if self.hash_auth(auth) != self.auth:
            return 0
        bet_amount = amount
        if bet_amount > self.money:
            bet_amount = self.money
            self.money = 0
        else:
            self.money -= bet_amount
        return bet_amount
    
    def new_hand(self, auth, hand:list):
        if self.hash_auth(auth) == self.auth:
            self.hand = hand
            return True
        return False
    
    def add_money(self, auth, amount_to_add:int):
        if self.hash_auth(auth) == self.auth:
            self.money += amount_to_add
            return True
        return False
    
    def get_name(self):
        return self.name
    
    def reveal_hand(self, auth):
        if self.hash_auth(auth) != self.auth:
            return []
        return self.hand
    
    @abstractmethod
    def compute_results(self, auth, tabled_cards:list, others_worth:list, pot:int, player_names:list, player_cards:list) -> None:
        if self.hash_auth(auth) != self.auth:
            return
        
    def get_results(self, auth, tabled_cards:list, others_worth:list, pot:int, player_names:list, player_cards:list) -> str:
        # print(auth)
        if self.hash_auth(auth) != self.auth:
            return self.name+"invalid hash:"+str(auth)
        try:
            self.compute_results(auth, tabled_cards=tabled_cards, others_worth=others_worth, pot=pot, player_names=player_names, player_cards=player_cards)
            return "successful computation"
        except Exception as e:
            return self.name+f" raised an error: {e}"

class human(player):
    @staticmethod
    def constructor(name, auth):
        return human(name, auth)

    def __get_input(self, call_amount:int):
        bet_amount = -1
        def valid_choice():
            if bet_amount >= call_amount or (bet_amount == self.money and bet_amount < call_amount) or bet_amount == 0:
                return True
            return False
        def error():
            say(f"Bet amount is not a valid amount. You have {self.money}.")
            say(f"To call requires {call_amount}.")
        while True:
            try:
                say((f"{self.name}, ({call_amount} to call): "))
                bet_amount = int(input())
            except:
                bet_amount = -1
            if valid_choice():
                break
            else:
                error()
        return bet_amount

    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        print(f"{self.name} has {self.money} moneys.")
        print(f"to call requires {call_amount}.")
        bet_amount = self.__get_input(call_amount)
        return bet_amount
    
    def reveal_hand(self, auth):
        if self.hash_auth(auth) != self.auth:
            return []
        hand = []
        say(f"enter {self.name}'s cards: ")
        while len(hand) < 2:
            add_to_list(hand)
        return hand

class random(player):
    @staticmethod
    def constructor(name, auth):
        return random(name, auth)

    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        call_perc = .5
        raise_perc = .25

        decision = np.random.random()
        print(f"random decision: {decision}")
        amount = 0
        if decision < call_perc:
            amount = min(call_amount, self.money)
        elif decision < call_perc + raise_perc:
            amount = np.random.randint(call_amount,self.money) if self.money > call_amount else self.money
        return amount

class raiser(player):
    @staticmethod
    def constructor(name, auth):
        return raiser(name,auth)
    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        call_multiplier = 1.1

        amount = int(call_amount*call_multiplier)+1
        if amount > self.money:
            amount = self.money
        return amount

class tracker(player):
    @staticmethod
    def constructor(name, auth):
        return tracker(name, auth)
    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        if not os.path.exists(self.name+"_tracker"):
            os.mkdir(self.name+"_tracker")
        for i,name in enumerate(player_names):
            path = os.path.join(self.name+"_tracker", name+".json")
            dump = {"call_amount":call_amount, "tabled_cards":tuple(tabled_cards), "worth":others_worth[i], "pot":pot, "bid":player_bids[i],}
            with open(path,'w') as file:
                json.dump(dump, file)
        
        return super().make_decision(auth=auth, call_amount=call_amount, tabled_cards=tabled_cards, others_worth=others_worth, pot=pot, player_bids=player_bids, player_turn=player_turn, player_names=player_names, folded_players=folded_players)
    
    def compute_results(self, auth, tabled_cards, others_worth, pot, player_names, player_cards):
        if self.hash_auth(auth) != self.auth:
            return 0
        # take a minute to finish results
        for i in range(10,-1,-1):
            print(i)
            time.sleep(1)
        for i,name in enumerate(player_names):
            path = os.path.join(self.name+"_tracker", name+".json")
            if not os.path.exists(path):
                raise RuntimeError(f"tracker {self.name} cannot find file for {name}")
            with open(path,'r') as file:
                print(self.name+str(json.load(file)))

class bayesian(player):
    @staticmethod
    def constructor(name, auth):
        return bayesian(name, auth)
    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        return super().make_decision(auth, call_amount, tabled_cards, others_worth, pot, player_bids, player_turn, player_names, folded_players)
    
    def compute_results(self, auth, tabled_cards:list, others_worth:list, pot:int, player_names:list, player_cards:list):
        if self.hash_auth(auth) != self.auth:
            return 0
        return super().compute_results(auth, tabled_cards, others_worth, pot, player_names, player_cards)

class expectation(player):
    MININTERVAL = 0.5
    @staticmethod
    def constructor(name, auth):
        return expectation(name, auth)
    
    def __num_opps_to_calculate(self, auth, num_tabled:int, num_players:int):
        if self.hash_auth(auth) != self.auth:
            return 0
        
        if num_tabled < 3:
            # this is pre-flop, only calculate tabled cards, not opponents cards
            return 0
        
        num_opps = num_players - 1

        num_cores = mp.cpu_count()
        num_calcs_per_core_per_sec = 10000
        max_seconds = 10
        cutoff = num_calcs_per_core_per_sec * max_seconds * num_cores
        
        base_calcs = comb(50-num_tabled, 5-num_tabled)
        num_total_calcs = base_calcs + sum([comb(45 - 2*i,2) for i in range(num_opps)])

        while num_total_calcs > cutoff:
            print("cannot calculate all players, dropping one")
            num_opps -= 1
            if num_players == 2:
                # we want to always calculate with at least one opponent 
                # (at least after the flop)
                break
            num_total_calcs = base_calcs + sum([comb(45 - 2*i,2) for i in range(num_opps-1)])
        
        return num_opps

    def __calculate_prob_win(self, auth, tabled_cards:list, num_players:int):
        if self.hash_auth(auth) != self.auth:
            return 0

        # get number of opponents to calculate for, based on how many combos we'd have to run through
        num_opps = self.__num_opps_to_calculate(auth, len(tabled_cards), num_players)
        num_opps = 0 # only for testing
        if num_opps == 0:
            # TODO: actually split probabilities across each type of hand for myself and the opponent
            cardsum = self.hand[0][0] + self.hand[1][0]
            return 1-((28-cardsum)/28)

        # generate possible tabled cards combos
        deck, _, _, _, _ = create_deck()
        for c in self.hand:
            deck.remove(c)
        for c in tabled_cards:
            deck.remove(c)
        
        cpus = mp.cpu_count()
        processes = []
        if len(tabled_cards) < 5:
            num_tabled_remaining = 5 - len(tabled_cards)
            future_tabled_combos = [list(c) for c in tqdm(combinations(deck, num_tabled_remaining),desc="creating combos",leave=False)]
            chunk_size = len(future_tabled_combos)//cpus
            q = mp.SimpleQueue()
            lock = mp.Lock()
            print(f" starting {cpus} processes...")
            for offset,i in enumerate(range(0,len(future_tabled_combos), chunk_size)):
                p = mp.Process()
                p.start()
                processes.append(p)
        elif len(tabled_cards) == 5:
            pass


        



    def __pre_river_win_tally(self, auth, tabled_cards:list, tabled_combos:list, deck:list, opps_to_calc:int, q:mp.SimpleQueue, offset:int, lock):
        if self.hash_auth(auth) != self.auth:
            return np.zeros(3)

        win_loss_tally = np.zeros(3)
        dummy_deck = deck.copy()
        lock.acquire()
        pbar= tqdm(total=len(tabled_combos), desc=f"chunk {offset}", position=offset, mininterval=self.MININTERVAL)
        lock.release()
        start = time.time()
        old = 0
        for i,c in enumerate(tabled_combos):
            if time.time() - start > self.MININTERVAL:
                lock.acquire()
                pbar.update(i-old)
                lock.release()
                old = i
                start = time.time()
            for card in c:
                dummy_deck.remove(card)
            selfhand = self.hand + tabled_cards + c
            selfres = calc_best_hand(selfhand)

    def __recursive_opp_calc(self, auth, deck:list, opps_res:list, opps_to_calc:int, q:mp.SimpleQueue):




    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        num_players = len(player_names) - sum(folded_players)
        prob_win = self.__calculate_prob_win(auth, tabled_cards=tabled_cards, num_players=num_players)
        max_expected_winnings = -np.inf
        expected_winnings_argmax = 0
        for i in range(self.money+1):
            expected_winnings = prob_win*(pot + sum(player_bids)) + (1-prob_win)*(-i)
            if expected_winnings > max_expected_winnings:
                max_expected_winnings = expected_winnings
                expected_winnings_argmax = i
        
        return expected_winnings_argmax

    
    def compute_results(self, auth, tabled_cards:list, others_worth:list, pot:int, player_names:list, player_cards:list):
        if self.hash_auth(auth) != self.auth:
            return 0
        return super().compute_results(auth, tabled_cards, others_worth, pot, player_names, player_cards)