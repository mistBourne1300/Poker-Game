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
            self.money = 0
        else:
            self.money -= bet_amount
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
            return None
        return self.hand
    



class human(player):
    @staticmethod
    def constructor(name, auth):
        return human(name, auth)

    def __get_input(self, call_amount:int):
        bet_amount = np.inf
        def valid_choice():
            if bet_amount >= call_amount or bet_amount == self.money or bet_amount == 0:
                return True
            return False
        def error():
            fancy_out(f"Bet amount is not a valid amount. You have {self.money}.")
            fancy_out(f"To call requires {call_amount}.")
        while True:
            try:
                bet_amount = int(input(f"{self.name}, enter bet amount ({call_amount} to call): "))
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
        fancy_out(f"You have {self.money}.")
        fancy_out(f"to call requires {call_amount}.")
        bet_amount = self.__get_input(call_amount)
        return bet_amount

class random(player):
    @staticmethod
    def constructor(name, auth):
        return random(name, auth)

    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        call_perc = .5
        raise_perc = .1

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
