import numpy as np
import time
from abc import ABC, abstractmethod
import os
import pickle
import multiprocessing as mp
import hashlib
import json
from scipy.special import softmax

from matplotlib import pyplot as plt

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
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        bet_amount = call_amount
        if bet_amount > self.money:
            bet_amount = self.money
        return bet_amount
    
    def decide(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        bet_amount = 0
        try:
            bet_amount = self.make_decision(auth=auth, call_amount=call_amount, tabled_cards=tabled_cards, others_worth=others_worth, pot=pot, player_bids=player_bids, player_turn=player_turn, player_names=player_names, folded_players=folded_players, last_raise_idx=last_raise_idx, prev_raise_idx=prev_raise_idx, bet_num=bet_num)
        except Exception as e:
            import traceback
            try:
                say(f"player {self.name} threw an error! This causes a fold.")
            except:
                print(f"player {self.name} threw an error! This causes a fold.")
            print(traceback.format_exc())
            bet_amount = 0
        print(f"bet amount: {bet_amount}")
        print(f"self money: {self.money}")

        max_others_worth = 0
        # TODO: this calculation includes folded players...
        for i,worth in enumerate(others_worth):
            if i == player_turn: continue
            if worth + player_bids[i] > max_others_worth:
                max_others_worth = worth + player_bids[i]
        
        if bet_amount + player_bids[player_turn] > max_others_worth:
            bet_amount = max_others_worth - player_bids[player_turn]
            try:
                print(f"player {self.name} bet more than everyone else has. truncating bet to maximum of other's worth")
            except:
                print(f"player {self.name} bet more than everyone else has. truncating bet to maximum of other's worth")

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
            return self.name+f" raised an error: {e}, {e.__traceback__}"
    



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

    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int) -> int:
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

    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int) -> int:
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
    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int) -> int:
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
    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        if not os.path.exists(self.name+"_tracker"):
            os.mkdir(self.name+"_tracker")
        for i,name in enumerate(player_names):
            path = os.path.join(self.name+"_tracker", name+".json")
            dump = {"call_amount":int(call_amount), "tabled_cards":tuple(tabled_cards), "worth":int(others_worth[i]), "pot":int(pot), "bid":int(player_bids[i])}
            with open(path,'w') as file:
                json.dump(dump, file,indent=1)
        
        return super().make_decision(auth=auth, call_amount=call_amount, tabled_cards=tabled_cards, others_worth=others_worth, pot=pot, player_bids=player_bids, player_turn=player_turn, player_names=player_names, folded_players=folded_players, last_raise_idx=last_raise_idx, prev_raise_idx=prev_raise_idx, bet_num=bet_num)
    
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

class expector(player):
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
            return min(num_players - 1,1)
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
        
        # if num_opps > 1 and len(tabled_cards) < 5:
        print(f"{self.name} calculating")
        speak_calculating = (len(tabled_cards) == 0) or (len(tabled_cards) < 5 and num_opps > 1)
        if speak_calculating:
            p = mp.Process(target=say, args = (f"{self.name} calculating",False))
            p.start()
        # say(f"{self.name} calculating")
            # except:
            #     print(f"{self.name} calculating")
        
        self.prev_full_hand = curr_full_hand

        self.prev_probs = calc_probs_multiple_opps(hand=self.hand, tabled=tabled_cards, num_opps=num_opps)
        np.nan_to_num(self.prev_probs[3],copy=False, nan=0.0, posinf=0.0, neginf=0.0)

        # self_hand_probs, opp_hand_probs, wl_probs = self.prev_probs
        if speak_calculating:
            p.kill()
            p.join()
            p.close()

        if num_opps != num_players - 1:
            if num_opps > 0:
                prob_win_against_true_opp_num = self.prev_probs[2][0]**((num_players - 1)/num_opps) # better estimate prob that we win
                within_hands_true_probs_win = self.prev_probs[3][:,0]**((num_players-1)/num_opps) # better estimate of within hands probs we win
            else:
                prob_win_against_true_opp_num = (self.prev_probs[2][0]**(num_players - 1)) # better estimate prob that we win
                within_hands_true_probs_win = self.prev_probs[3][:,0]**(num_players - 1) # better estimate of within hands probs we win
            missing_prob = self.prev_probs[2][0] - prob_win_against_true_opp_num # get difference between old estimate and better estimae
            self.prev_probs[2][0] = prob_win_against_true_opp_num # make the prob we win the better estimate
            self.prev_probs[2][1] += missing_prob # give the prob we lose the difference

            missing_probs = self.prev_probs[3][:,0] - within_hands_true_probs_win
            self.prev_probs[3][:,0] = within_hands_true_probs_win
            self.prev_probs[3][:,1] = missing_probs



        return self.prev_probs

    def get_choice(self,auth,call_amount,tabled_cards,pot,player_bids,probs):
        if self.hash_auth(auth) != self.auth:
            return 0
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
        pos_expected_winnings = expected_winnings[expected_winnings>0]
        if len(pos_expected_winnings) > 0:
            expected_winnings_argmax = np.argmax(pos_expected_winnings)
            max_expected_winnings = pos_expected_winnings[expected_winnings_argmax]
            [print(f"bet: {i+call_amount}, E[{(i+call_amount)}]: {e}") for i,e in enumerate(pos_expected_winnings)]
            bet_choice_probs = pos_expected_winnings**2
            print("pre softmax bet probs:")
            [print(f"bet: {i+call_amount}, p: {p}") for i,p in enumerate(bet_choice_probs)]
            bet_choice_probs = pos_expected_winnings**2
            bet_choice_probs = softmax(pos_expected_winnings**2)
            print("post softmax bet probs:")
            [print(f"bet: {i+call_amount}, p: {p}") for i,p in enumerate(bet_choice_probs)]
            choice = call_amount + np.random.choice([i for i in range(len(bet_choice_probs))],p=bet_choice_probs)
        elif len(expected_winnings) > 0:
            expected_winnings_argmax = np.argmax(expected_winnings)
            max_expected_winnings = expected_winnings[expected_winnings_argmax]
            [print(f"bet: {i+call_amount}, E[{(i+call_amount)}]: {e}") for i,e in enumerate(expected_winnings)]
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

    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0
        num_players = len(player_names) - sum(folded_players)
        _,_,probs,_ = self.calculate_probs(auth, tabled_cards=tabled_cards, num_players=num_players)
        return self.get_choice(auth=auth,call_amount=call_amount,tabled_cards=tabled_cards,pot=pot,player_bids=player_bids,probs=probs)

    
    def compute_results(self, auth, tabled_cards:list, others_worth:list, pot:int, player_names:list, player_cards:list):
        if self.hash_auth(auth) != self.auth:
            return 0
        return super().compute_results(auth, tabled_cards, others_worth, pot, player_names, player_cards)

class ratio(expector):
    def __init__(self,name:str,auth):
        super().__init__(name,auth)
        self.prev_full_hand = []
        self.prev_probs = np.ones(3)/3
    
    @staticmethod
    def constructor(name, auth):
        return ratio(name, auth)

    def get_choice(self,auth,call_amount,tabled_cards,pot,player_bids,probs):
        if self.hash_auth(auth) != self.auth:
            return 0
        max_expected_winnings = 0.0
        expected_winnings_argmax = 0

        num_betting_rounds_left = 4
        if len(tabled_cards) == 3:
            num_betting_rounds_left = 3
        elif len(tabled_cards) == 4:
            num_betting_rounds_left = 2
        elif len(tabled_cards) == 5:
            num_betting_rounds_left = 1
        
        expected_pot = pot + num_betting_rounds_left*sum(player_bids)
        expected_winnings = np.array([probs[0]*(expected_pot) + probs[1]*(-i) + probs[2]*(expected_pot + i)/2 for i in range(call_amount,self.money)])
        expected_loss_ratios = np.array([probs[0]*(-(expected_pot)/(self.money + expected_pot)) + probs[1]*(i/(self.money - i)) + probs[2]*(-expected_pot/(2*self.money + expected_pot)) for i in range(call_amount,self.money)])
        pos_expected_winnings = expected_winnings[(expected_loss_ratios<0) & (expected_winnings>0)]

        expected_loss_ratios = expected_loss_ratios[expected_loss_ratios<0]

        only_expected_winnings = expected_winnings[expected_winnings > 0]
        
        if len(pos_expected_winnings) > 0:
            expected_winnings_argmax = np.argmax(pos_expected_winnings)
            max_expected_winnings = pos_expected_winnings[expected_winnings_argmax]
            [print(f"bet: {i+call_amount}, E[{(i+call_amount)}]: {e}") for i,e in enumerate(pos_expected_winnings)]
            bet_choice_probs = [val**2 for i,val in enumerate(pos_expected_winnings)]
            print("pre softmax bet probs:")
            [print(f"bet: {i+call_amount}, p: {p}") for i,p in enumerate(bet_choice_probs)]
            bet_choice_probs = softmax(bet_choice_probs)
            print("post softmax bet probs:")
            [print(f"bet: {i+call_amount}, p: {p}") for i,p in enumerate(bet_choice_probs)]
            if probs[0] < 1e-5:
                choice = 0
            else:
                choice = call_amount + np.random.choice([i for i in range(len(bet_choice_probs))],p=bet_choice_probs)
        elif len(expected_loss_ratios) > 0:
            print("in general expected_loss_ratios")
            expected_loss_argmin = np.argmin(expected_loss_ratios)
            min_expected_loss = expected_loss_ratios[expected_loss_argmin]
            [print(f"bet: {i+call_amount}, E[{(i+call_amount)}]: {e}") for i,e in enumerate(expected_loss_ratios)]
            if min_expected_loss < 0:
                choice = call_amount + expected_loss_argmin
            else:
                choice = 0
        elif len(only_expected_winnings) > 0:
            print("in only_expected_winnings")
            only_expected_winnings_argmax = np.argmax(only_expected_winnings)
            max_only_expected_winnings = only_expected_winnings[only_expected_winnings_argmax]
            [print(f"bet: {i+call_amount}, E[{(i+call_amount)}]: {e}") for i,e in enumerate(only_expected_winnings)]
            if max_only_expected_winnings > 0:
                choice = call_amount + only_expected_winnings_argmax
            else:
                choice = 0
        else:
            # we have to decide whether to go all in here
            # because the call amount is more money than we have
            choice = self.money
            # expected_winnings = expected_winnings[expected_winnings>0]
            expected_winnings = np.array([probs[0]*(expected_pot) + probs[1]*(-i) + probs[2]*(expected_pot + i)/2 for i in range(call_amount,self.money+1)])
            if len(expected_winnings) > 0:
                max_expected_winnings = np.max(expected_winnings)
            else:
                max_expected_winnings = probs[0]*expected_pot+ probs[1]*(-self.money) + probs[2]*(expected_pot + self.money)/2
            if max_expected_winnings <= 0:
                choice = 0
        
        print(f"probs: {probs}")
        print(f"max expected winnings: {max_expected_winnings}")

        return choice
    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int):
        if self.hash_auth(auth) != self.auth:
            return 0
        num_players = len(player_names) - sum(folded_players)
        _,_,probs,_ = self.calculate_probs(auth, tabled_cards=tabled_cards, num_players=num_players)
        return self.get_choice(auth=auth,call_amount=call_amount,tabled_cards=tabled_cards,pot=pot,player_bids=player_bids,probs=probs)
        
# TODO: somehow check whether someone checked (and thus bet 0) or if they just haven't had the chance to bet until now
class bayesian(ratio):
    def __init__(self, name, auth, bayes_avg=False, ignore_ties=False):
        super().__init__(name, auth)
        self.prev_probs = (np.ones(10)/10, np.ones(10)/10, np.ones(3)/3)
        self.folder = self.name+"_bayes"
        self.temp_filename = "temp.json"
        self.database_filename = "data.json"
        self.bayes_avg = bayes_avg
        self.ignore_ties = ignore_ties

    @staticmethod
    def constructor(name, auth, bayes_avg=False, ignore_ties=False):
        return bayesian(name, auth, bayes_avg, ignore_ties)
    
    def get_bayesian_wl_probs(self,auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int):
        if self.hash_auth(auth) != self.auth:
            return 0

        num_players = len(player_names) - sum(folded_players)
        self_hand_probs, opp_hand_probs, wl_probs, within_hands_wl_probs = self.calculate_probs(auth=auth, tabled_cards=tabled_cards, num_players=num_players)
        # if np.allclose(opp_hand_probs,np.zeros_like(opp_hand_probs)):
        #     # we only computed the self probs, we need to 
        tie_prob = wl_probs[-1]
        

        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

        
        if not os.path.exists(os.path.join(self.folder,self.temp_filename)):
            temp_data = dict()
            for i,name in enumerate(player_names):
                if i==player_turn:
                    continue
                temp_data[name] = {"pre-flop":{"called":tuple(),"raised":tuple()},"post-flop pre-turn":{"called":tuple(),"raised":tuple()},"post-turn pre-river":{"called":tuple(),"raised":tuple()},"post-river":{"called":tuple(),"raised":tuple()}}
        else:
            # if this is pre-flop, we shouldn't have any temp info. 
            # if we do it's from the last round, and compute_results() never got called to clean it up 
            # we need to remove this old data
            if len(tabled_cards) == 0:
                os.remove(os.path.join(self.folder,self.temp_filename))
                temp_data = dict()
                for i,name in enumerate(player_names):
                    if i==player_turn:
                        continue
                    temp_data[name] = {"pre-flop":{"called":tuple(),"raised":tuple()},"post-flop pre-turn":{"called":tuple(),"raised":tuple()},"post-turn pre-river":{"called":tuple(),"raised":tuple()},"post-river":{"called":tuple(),"raised":tuple()}}
            else:
                # load temp_data object to append to
                try:
                    with open(os.path.join(self.folder,self.temp_filename),'r+') as temp_file:
                        temp_data = json.load(temp_file)
                except:
                    temp_data = dict()
                for i,name in enumerate(player_names):
                    if name not in temp_data:
                        temp_data[name] = {"pre-flop":{"called":tuple(),"raised":tuple()},"post-flop pre-turn":{"called":tuple(),"raised":tuple()},"post-turn pre-river":{"called":tuple(),"raised":tuple()},"post-river":{"called":tuple(),"raised":tuple()}}
        
        for name in player_names:
            player_path = os.path.join(self.folder,name)
            if not os.path.exists(player_path):
                os.mkdir(player_path)
                json_file_path = os.path.join(player_path,self.database_filename)
                obj = {"pre-flop":{"called":dict(),"raised":dict()},"post-flop pre-turn":{"called":dict(),"raised":dict()},"post-turn pre-river":{"called":dict(),"raised":dict()},"post-river":{"called":dict(),"raised":dict()}}
                with open(json_file_path,"w") as file:
                    json.dump(obj,file, indent=1)
        

        betting_round = ""
        if len(tabled_cards) == 0:
            betting_round = "pre-flop"
        elif len(tabled_cards) == 3:
            betting_round = "post-flop pre-turn"
        elif len(tabled_cards) == 4:
            betting_round = "post-turn pre-river"
        elif len(tabled_cards) == 5:
            betting_round = "post-river"
        else:
            raise RuntimeError("there are an invalid number of cards on the table")


        total_game_money = np.sum(player_bids) + np.sum(others_worth) + pot

        
        

        # loop through each player, getting the worse-case scenario for us (smallest win probability)
        for i in range(len(player_names)):
            if folded_players[i]:
                continue
            if i==player_turn:
                continue
            
            
            # get the proportion of the total game value held by this player
            player_moneys = others_worth[i] + player_bids[i]
            lamb = player_moneys/total_game_money

            player_name = player_names[i]
            player_bid = player_bids[i]
            player_path = os.path.join(self.folder,player_name)
            player_bid_type = "raised" if i == last_raise_idx else "called"

            with open(os.path.join(player_path,self.database_filename)) as datafile:
                player_data = json.load(datafile)
                current_betting_dict = player_data[betting_round][player_bid_type]
                if player_bid_type == 'raised':
                    bid_str = str(player_bid - player_bids[prev_raise_idx])
                else:
                    bid_str = str(player_bid)
                if bid_str in current_betting_dict:
                    current_betting_data = current_betting_dict[bid_str]
                else:
                    current_betting_data = None
            
            if current_betting_data is not None:
                # do we want to do a sum here, which puts more weight into the player's betting history,
                # or do we want to do an average, which puts more weight into the current hand?
                if self.bayes_avg:
                    print("BAYES AVG IS ON")
                    numpy_betting_data = np.mean(current_betting_data,axis=0)
                else:
                    numpy_betting_data = np.sum(current_betting_data,axis=0)
            else:
                numpy_betting_data = np.zeros_like(opp_hand_probs)
        
            # compute alphas, scaling 
            if player_moneys == 0:
                # if they have nothing left, we don't consider their previous data to be relevant 
                # (better players will have more meaningful data, and also more money in the game)
                alphas = opp_hand_probs
            else:
                alphas = opp_hand_probs/lamb + numpy_betting_data
            
            # here we are adding one to each alpha, to satisfy the unique mode constraint, 
            # but then we also subtract one from each alpha, so the net is 0
            print(f"opp_hand_probs: {opp_hand_probs}")
            print(f"lamb: {lamb}")
            print(f"numpy data: {numpy_betting_data}")
            print(f"alpha: {alphas}")
            modes = alphas/(np.sum(alphas))
            
            # create a prob matrix
            prob_matrix = np.zeros((10,10))
            for i,self_prob in enumerate(self_hand_probs):
                for ii,opp_prob in enumerate(modes):
                    prob_matrix[i,ii] = self_prob*opp_prob

            tie_probs = np.diag(prob_matrix)
            tie_prob = np.sum(tie_probs)
            win_prob = np.sum(np.tril(prob_matrix)) - tie_prob
            loss_prob = np.sum(np.triu(prob_matrix)) - tie_prob
            tie_prob = 0.0
            print("within_hand_wl_probs:")
            print(within_hands_wl_probs)
            print()
            for i,p in enumerate(tie_probs):
                if np.any(within_hands_wl_probs[i,:]==np.nan) or np.any(within_hands_wl_probs[i,:]==np.inf) or np.any(within_hands_wl_probs[i,:]==-np.inf):
                    continue
                win_prob += p*within_hands_wl_probs[i,0]
                loss_prob += p*within_hands_wl_probs[i,1]
                tie_prob += p*within_hands_wl_probs[i,2]
            new_wl_probs = np.array([win_prob,loss_prob,tie_prob])
            
            # since we're playing to win, we need to do our calculations with the worst-case scenario
            if new_wl_probs[0] < wl_probs[0] and not (np.any(new_wl_probs==np.nan) or np.any(new_wl_probs==np.inf) or np.any(new_wl_probs==-np.inf)):
                wl_probs = new_wl_probs
            
            # append the current bid to the appropriate tuple
            old_tuple = temp_data[player_name][betting_round][player_bid_type]
            new_tuple = (*old_tuple,int(player_bid))
            temp_data[player_name][betting_round][player_bid_type] = new_tuple

        
        # after all player bids have been updated, we save the temp_data object back to storage
        try:
            with open(os.path.join(self.folder,self.temp_filename),'w') as temp_file:
                json.dump(temp_data,temp_file,indent=1)
        except Exception as e:
            print(f"we have thrown an error: {e}")
            print(e.__traceback__)
            print()
            print("the current temp_data object:")
            print(temp_data)
            time.sleep(10)
        wl_probs[-1] = tie_prob
        return wl_probs

    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int) -> int:
        if self.hash_auth(auth) != self.auth:
            return 0

        
        probs = self.get_bayesian_wl_probs(auth=auth, call_amount=call_amount, tabled_cards=tabled_cards, others_worth=others_worth, pot=pot, player_bids=player_bids, player_turn=player_turn, player_names=player_names, folded_players=folded_players, last_raise_idx=last_raise_idx, prev_raise_idx=prev_raise_idx, bet_num=bet_num)
        # here we experiment...
        if self.ignore_ties:
            print("IGNORE TIES IS ON")
            probs[-1] = 0
            probs = probs/np.sum(probs)
        return self.get_choice(auth=auth,call_amount=call_amount,tabled_cards=tabled_cards,pot=pot,player_bids=player_bids,probs=probs)       

    def compute_results(self, auth, tabled_cards:list, others_worth:list, pot:int, player_names:list, player_cards:list):
        if self.hash_auth(auth) != self.auth:
            return 0
        
        if not os.path.exists(os.path.join(self.folder,self.temp_filename)):
            print(f"{self.name} cannot find it's temp data file...")
            return
        try:
            with open(os.path.join(self.folder,self.temp_filename)) as temp_file:
                temp_data = json.load(temp_file)
        except:
            print("could not read from temp file")
            return
        
        for i in range(len(player_names)):
            player_name = player_names[i]
            player_hand = player_cards[i]
            if player_hand is None:
                continue # the player folded, and did not reveal their cards
            player_path = os.path.join(self.folder,player_name)
            temp_player_dict = temp_data[player_name]

            
            if not os.path.exists(os.path.join(player_path,self.database_filename)):
                print(f"{self.name} cannot find data file for {player_name}")
                continue

            with open(os.path.join(player_path,self.database_filename),"r+") as datafile:
                player_data = json.load(datafile)

            for betting_round in temp_player_dict.keys():
                betting_round_dict = temp_player_dict[betting_round]
                if betting_round == "pre-flop":
                    tables = []
                elif betting_round == "post-flop pre-turn":
                    tables = tabled_cards[:3]
                elif betting_round == "post-turn pre-river":
                    tables = tabled_cards[:4]
                elif betting_round == "post-river":
                    tables = tabled_cards
                else:
                    raise RuntimeError(f"betting round {betting_round} is not valid!")
                
                
                player_hand_opps,_,_,_ = calc_probs_multiple_opps(hand=player_hand, tabled=tables, num_opps=0)
                for bet_type in betting_round_dict.keys():
                    bet_type_tuple = betting_round_dict[bet_type]
                    for bet_amount in bet_type_tuple:
                        if bet_amount in player_data[betting_round][bet_type]:
                            bet_amount_tuples = player_data[betting_round][bet_type][bet_amount]
                            player_data[betting_round][bet_type][bet_amount] = (*bet_amount_tuples, tuple(player_hand_opps))
                        else:
                            player_data[betting_round][bet_type][bet_amount] = tuple((tuple(np.zeros_like(player_hand_opps)),tuple(player_hand_opps)))
            
            with open(os.path.join(player_path,self.database_filename),"w") as datafile:
                json.dump(player_data,datafile,indent=1)
        os.remove(os.path.join(self.folder,self.temp_filename))
            

        

class external_func(player):
    # TODO: implement some external functions and see if this works
    """
        this class takes in two functions that become the make_decsion and compute_results functions for the player
        it achieves this by overriding these functions with a method that's passed in
    """
    def __init__(self,name:str, auth, decision_function:callable=None, compute_function:callable=None):
        super().__init__(name,auth)
        if decision_function is not None:
            self.make_decision = decision_function
        if compute_function is not None:
            self.compute_results = compute_function
    
    @staticmethod
    def constructor(name:str, auth, decision_function:callable=None, compute_function:callable=None):
        return external_func(name, auth, decision_function, compute_function)


class folder(player):
    @staticmethod
    def constructor(name, auth):
        return folder(name, auth)
    
    def make_decision(self, auth, call_amount:int, tabled_cards:list, others_worth:list, pot:int, player_bids:list, player_turn:int, player_names:list, folded_players:list, last_raise_idx:int, prev_raise_idx:int, bet_num:int):
        if len(player_names) > 2:
            return 0 # if there is more than one other person, fold
        return self.money # otherwise, go all in
    
    def compute_results(self, auth, tabled_cards:list, others_worth:list, pot:int, player_names:list, player_cards:list):
        return super().compute_results(auth, tabled_cards, others_worth, pot, player_names, player_cards)
    
