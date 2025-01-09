import numpy as np
import time
from abc import ABC, abstractmethod
import os
import pickle

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
        hashable = str(pickle.dumps(auth))
        return hash(hashable)

    @abstractmethod
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        bet_amount = call_amount
        if bet_amount > self.money:
            bet_amount = self.money
        return bet_amount
    
    def decide(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        bet_amount = 0
        try:
            bet_amount = self.make_decision(auth=auth, call_amount=call_amount, tabled_cards=tabled_cards, others_worth=others_worth, pot=pot, player_bids=player_bids, player_turn=player_turn)
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
                say((f"{self.name}, enter bet amount ({call_amount} to call): "))
                bet_amount = int(input())
            except:
                bet_amount = np.inf
            if valid_choice():
                break
            else:
                error()
        return bet_amount

    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        say(f"{self.name} has {self.money} moneys.")
        say(f"to call requires {call_amount}.")
        bet_amount = self.__get_input(call_amount)
        return bet_amount
    
    def reveal_hand(self, auth):
        if self.hash_auth(auth) != self.auth:
            return []
        hand = []
        say(f"enter {self.name}'s cards: ")
        add_to_list(hand)
        return hand

class random(player):
    @staticmethod
    def constructor(name, auth):
        return random(name, auth)

    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        call_perc = .7
        raise_perc = .2

        decision = np.random.random()
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
    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int) -> int:
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

class expector(player):
    @staticmethod
    def constructor(name, auth):
        return expector(name, auth)
    
    def __num_opps_to_calculate(self, auth, num_tabled:int, num_players:int):
        if self.hash_auth(auth) != self.auth:
            return 0
        
        if num_tabled < 3:
            # this is pre-flop, only calculate tabled cards, not opponents cards
            return 0
        elif num_tabled == 5:
            # this is the final calculation, we should get the most accurate probabilities we can
            return num_players - 1
        
        num_opps = num_players - 1

        num_cores = mp.cpu_count()
        num_calcs_per_core_per_sec = 50000 # this number is specific to each computer, it will not 
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


    def __calculate_probs(self, auth, tabled_cards:list, num_players:int):
        if self.hash_auth(auth) != self.auth:
            return 0
        num_opps = self.__num_opps_to_calculate(auth=auth, num_tabled=len(tabled_cards), num_players=num_players)

        return calc_probs_multiple_opps(hand=self.hand, tabled=tabled_cards, num_opps=num_opps)




    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        num_players = len(player_names) - sum(folded_players)
        probs = self.__calculate_probs(auth, tabled_cards=tabled_cards, num_players=num_players)
        max_expected_winnings = -np.inf
        expected_winnings_argmax = 0
        for i in range(self.money+1):
            #                   prob of win * amount won       prob loss * amount lost    assuming a two-way tie here, since 3 or more is quite unlikely
            expected_winnings = probs[0]*(pot + sum(player_bids)) + probs[1]*(-i) + probs[2]*(pot + sum(player_bids) + i)/2
            if expected_winnings > max_expected_winnings:
                max_expected_winnings = expected_winnings
                expected_winnings_argmax = i
        
        return expected_winnings_argmax

    
    def compute_results(self, auth, tabled_cards:list, others_worth:list, pot:int, player_names:list, player_cards:list):
        if self.hash_auth(auth) != self.auth:
            return 0
        return super().compute_results(auth, tabled_cards, others_worth, pot, player_names, player_cards)