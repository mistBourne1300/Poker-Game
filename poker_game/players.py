import numpy as np
import time
from abc import ABC, abstractmethod
import os
import pickle
import hashlib
import json
from scipy.special import softmax

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
        self.hand = []
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
            say(f"player {self.name} threw an error! This causes a fold.")
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
        bet_amount = call_amount
        def valid_choice():
            if bet_amount >= call_amount or (bet_amount == self.money and bet_amount < call_amount) or bet_amount == 0:
                return True
            return False
        def error():
            say(f"Bet amount is not a valid amount. You have {self.money}.")
            say(f"To call requires {call_amount}.")
        while True:
            try:
                if call_amount > 0:
                    say((f"{self.name} ({call_amount} to call): "))
                else:
                    say((f"{self.name} (enter to check): "))
                bet_amount = int(input())
            except:
                bet_amount = call_amount
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
        self.hand = []
        while len(self.hand) < 2:
            say(f"enter {self.name}'s cards: ")
            print(f"current hand: {[tuple_to_str(c) for c in self.hand]}")
            add_to_list(self.hand,max_size=2)
        return self.hand

class random(player):
    @staticmethod
    def constructor(name, auth):
        return random(name, auth)

    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        call_perc = .7
        raise_perc = .2

        decision = np.random.random()
        amount = 0
        if decision < call_perc:
            amount = min(call_amount, self.money)
        elif decision < call_perc + raise_perc:
            probability_dist = np.arange(call_amount,self.money+1)
            probability_dist = probability_dist+1
            probability_dist = probability_dist**2
            probability_dist = probability_dist[::-1]/np.sum(probability_dist)
            

            amount = np.random.choice([i for i in range(call_amount,self.money+1)], p=probability_dist) if self.money > call_amount else self.money
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
            dump = {"call_amount":int(call_amount), "tabled_cards":tuple(tabled_cards), "worth":int(others_worth[i]), "pot":int(pot), "bid":int(player_bids[i])}
            with open(path,'w') as file:
                json.dump(dump, file)
        
        return super().make_decision(auth=auth, call_amount=call_amount, tabled_cards=tabled_cards, others_worth=others_worth, pot=pot, player_bids=player_bids, player_turn=player_turn, player_names=player_names, folded_players=folded_players)
    
    def compute_results(self, auth, tabled_cards, others_worth, pot, player_names, player_cards):
        if self.hash_auth(auth) != self.auth:
            return 0
        # take a minute to finish results
        # for i in range(10,-1,-1):
        #     print(i)
        #     time.sleep(1)
        for i,name in enumerate(player_names):
            path = os.path.join(self.name+"_tracker", name+".json")
            if not os.path.exists(path):
                raise RuntimeError(f"tracker {self.name} cannot find file for {name}")
            with open(path,'r') as file:
                print(self.name+str(json.load(file)))

class expector(player):
    EXPONENT = 2

    def __init__(self, name:str, auth):
        super().__init__(name,auth)
        self.prev_full_hand = []
        self.prev_probs = np.ones(3)/3


    

    @staticmethod
    def constructor(name, auth):
        return expector(name, auth)
    
    def num_opps_to_calculate(self, auth, num_tabled:int, num_players:int):
        if self.hash_auth(auth) != self.auth:
            return 0
        
        if num_tabled < 3:
            # this is pre-flop, only calculate tabled cards, not opponents cards
            return 0
        elif num_tabled == 3:
            return 1
        elif num_tabled == 4:
            return min(num_players - 1,2)
        elif num_tabled == 5:
            # this is the final calculation, we should get the most accurate probabilities we can
            return min(num_players - 1,2)


    def calculate_probs(self, auth, tabled_cards:list, num_players:int):
        if self.hash_auth(auth) != self.auth:
            return 0
        num_opps = self.num_opps_to_calculate(auth=auth, num_tabled=len(tabled_cards), num_players=num_players)


        curr_full_hand = self.hand + tabled_cards
        if self.prev_full_hand == curr_full_hand:
            return self.prev_probs
        
        if num_opps > 1 and len(tabled_cards) < 5:
            say(f"{self.name} calculating")
        
        self.prev_full_hand = curr_full_hand

        self.prev_probs = calc_probs_multiple_opps(hand=self.hand, tabled=tabled_cards, num_opps=num_opps)

        if num_opps != num_players - 1:
            if num_opps > 0:
                prob_win_against_true_opp_num = (self.prev_probs[0]**((num_players - 1)/num_opps))
            else:
                prob_win_against_true_opp_num = (self.prev_probs[0]**(num_players - 1))
            missing_prob = self.prev_probs[0] - prob_win_against_true_opp_num
            self.prev_probs[0] = prob_win_against_true_opp_num
            self.prev_probs[1] += missing_prob

        return self.prev_probs


    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        num_players = len(player_names) - sum(folded_players)
        probs = self.calculate_probs(auth, tabled_cards=tabled_cards, num_players=num_players)
        max_expected_winnings = 0.0
        expected_winnings_argmax = 0

        num_betting_rounds_left = 4
        if len(tabled_cards) == 3:
            num_betting_rounds_left = 3
        elif len(tabled_cards) == 4:
            num_betting_rounds_left = 2
        elif len(tabled_cards) == 5:
            num_betting_rounds_left = 1
        
        expected_winnings = np.array([probs[0]*(pot + num_betting_rounds_left*sum(player_bids)) + probs[1]*(-i) + probs[2]*(pot + num_betting_rounds_left*sum(player_bids) + i)/2 for i in range(call_amount,self.money+1)])
        expected_winnings_to_the_fourth = np.array([probs[0]*(pot + num_betting_rounds_left*sum(player_bids)) + probs[1]*(-(i**self.EXPONENT)) + probs[2]*(pot + num_betting_rounds_left*sum(player_bids) + i**self.EXPONENT)/2 for i in range(call_amount,self.money+1)])
        pos_expected_winnings = expected_winnings_to_the_fourth[expected_winnings>0]
        if len(pos_expected_winnings) > 0:
            expected_winnings_argmax = np.argmax(pos_expected_winnings)
            max_expected_winnings = pos_expected_winnings[expected_winnings_argmax]
            [print(f"bet: {i+call_amount}, E[{(i+call_amount)**4}]: {e}") for i,e in enumerate(pos_expected_winnings)]
            bet_choice_probs = softmax(pos_expected_winnings)
            choice = call_amount + np.random.choice([i for i in range(len(bet_choice_probs))],p=bet_choice_probs)
        elif len(expected_winnings) > 0:
            expected_winnings_argmax = np.argmax(expected_winnings)
            max_expected_winnings = expected_winnings[expected_winnings_argmax]
            [print(f"bet: {i+call_amount}, expectation: {e}") for i,e in enumerate(expected_winnings)]
            choice = 0
        else:
            # we have to decide whether to go all in here
            # because the call amount is more money than we have
            choice = self.money
            expected_winnings = probs[0]*(pot + num_betting_rounds_left*sum(player_bids)) + probs[1]*(-choice) + probs[2]*(pot + num_betting_rounds_left*sum(player_bids) + choice)/2
            max_expected_winnings = expected_winnings
            if expected_winnings < 0:
                # we fold
                choice = 0
        print(f"probs: {probs}")
        print(f"max expected winnings: {max_expected_winnings}")

        
            
        
        
        return choice

    
    def compute_results(self, auth, tabled_cards:list, others_worth:list, pot:int, player_names:list, player_cards:list):
        if self.hash_auth(auth) != self.auth:
            return 0
        return super().compute_results(auth, tabled_cards, others_worth, pot, player_names, player_cards)

class bayesian(expector):
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
