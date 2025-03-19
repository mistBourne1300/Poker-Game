import numpy as np
import time
import utils
import multiprocessing as mp
from multiprocessing.pool import ThreadPool
from threading import Thread
import os
import argparse

from players import *
from utils import *
from enum import Enum

class mode(Enum):
    """ 
        A simple enum.
        HYBRID_PLAY is where all human players are playing a game with real cards, and any AI opponent's cards are input to the computer
        COMPUTER_ONLY is solely AI opponents, and is mostly a testing ground
    """
    HYBRID_PLAY = 1
    COMPUTER_ONLY = 2

class table:
    def __init__(self, player_constructors:list, player_names:list, starting_money:int, small_blind:int=1, big_blind:int=None, say:callable=utils.say, verbose=True):
        assert len(player_constructors) == len(player_names)
        if big_blind is None:
            big_blind = small_blind*2
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.players = []
        self.auths = []
        self.MODE = mode.COMPUTER_ONLY
        self.say = say
        self.first_round = True
        self.v = verbose
        for i,constructor in enumerate(player_constructors):
            if self.v: print(i,player_names[i])
            auth = np.random.randint(1000000)
            self.auths.append(auth)
            new_player = constructor(player_names[i],auth)
            new_player.add_money(auth, starting_money)
            if isinstance(new_player, human):
                self.MODE = mode.HYBRID_PLAY
            self.players.append(new_player)
        self.prev_raise_idx = 0
    
    def initiate_blinds(self, dealer_idx):
        current_bids = [0]*len(self.players)
        player_max_earnings = [np.inf]*len(self.players)

        small_blind_index = (dealer_idx+1)%len(self.players)
        big_blind_index = (dealer_idx+2)%len(self.players)

        small_blind_auth = self.auths[small_blind_index]
        big_blind_auth = self.auths[big_blind_index]

        small_blind_player = self.players[small_blind_index]
        big_blind_player = self.players[big_blind_index]
        
        current_raise = self.big_blind

        current_bids[small_blind_index] = small_blind_player.blind(small_blind_auth, self.small_blind)
        if current_bids[small_blind_index] < self.small_blind or small_blind_player.worth() == 0:
            player_max_earnings[small_blind_index] = current_bids[small_blind_index]*len(self.players)
            self.say(f"{small_blind_player.get_name()} is all in with {current_bids[small_blind_index]} for small blind.\nTheir max earning potential is now {player_max_earnings[small_blind_index]}")
        utils.confirm(f"{small_blind_player.get_name()} pays small blind of {current_bids[small_blind_index]}") if self.MODE == mode.HYBRID_PLAY else self.say(f"{small_blind_player.get_name()} pays small blind of {current_bids[small_blind_index]}")

        current_bids[big_blind_index] = big_blind_player.blind(big_blind_auth, self.big_blind)
        if current_bids[big_blind_index] < self.big_blind or big_blind_player.worth() == 0:
            player_max_earnings[big_blind_index] = current_bids[big_blind_index]*len(self.players)
            self.say(f"{big_blind_player.get_name()} is all in with {current_bids[big_blind_index]} for big blind.\nTheir max earning potential is now {player_max_earnings[big_blind_index]}")
        if current_bids[big_blind_index] < self.big_blind:
            if len(self.players) == 2:
                self.say(f"since there are only 2 players, and one is all in, bet amount is now {max(current_bids)}")
                current_raise = max(current_bids)
            else:
                self.say(f"bet amount is still {self.big_blind}")
        utils.confirm(f"{big_blind_player.get_name()} pays big blind of {current_bids[big_blind_index]}") if self.MODE == mode.HYBRID_PLAY else self.say(f"{big_blind_player.get_name()} pays big blind of {current_bids[big_blind_index]}") 


        return current_bids, player_max_earnings, current_raise
    
    def num_betting_players(self, folded_players:list, player_max_earnings:list):
        return len(self.players) - sum(folded_players) - sum([(earning_potential < np.inf) for earning_potential in player_max_earnings])
    
    def pre_flop_bet(self, dealer_idx):
        current_bids,player_max_earnings, current_raise = self.initiate_blinds(dealer_idx)
        # current_raise = self.big_blind
        last_raise_idx = (dealer_idx+2)%len(self.players)
        big_blind_idx = last_raise_idx
        self.prev_raise_idx = (dealer_idx+1)%len(self.players)
        current_player_idx = (dealer_idx+3)%len(self.players)
        folded_players = [False]*len(self.players)
        pot = 0
        roundabout = 0
        confirm_needed = True
        # if self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings) == 1:
        #     pot = sum(current_bids)
        #     return pot, folded_players, player_max_earnings, last_raise_idx

        while current_player_idx != big_blind_idx:
            confirm_needed = True
            # if self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings) <= 1 and current_bids[current_player_idx] == current_raise:
            #     break
            if folded_players[current_player_idx] or player_max_earnings[current_player_idx]<np.inf:
                # the player has either folded, or has gone all in. In either case, we continue to the next player
                if self.v: print(f"{self.players[current_player_idx].get_name()} cannot bet")
                current_player_idx = (current_player_idx+1)%len(self.players)
                continue
            if self.v: print(f"\n{self.players[current_player_idx].get_name()}'s turn")
            current_auth = self.auths[current_player_idx]
            current_player = self.players[current_player_idx]
            call_amount = current_raise - current_bids[current_player_idx]
            others_worth = [player.worth() for player in self.players]
            player_bid = current_player.decide(auth=current_auth, call_amount=call_amount, tabled_cards=[], others_worth=others_worth, pot=0, player_bids=current_bids, player_turn=current_player_idx, player_names=[player.get_name() for player in self.players], folded_players=folded_players, last_raise_idx=last_raise_idx, prev_raise_idx = self.prev_raise_idx)
            
            if player_bid < call_amount:
                if current_player.worth() > 0:
                    folded_players[current_player_idx] = True
                    current_player_idx = (current_player_idx+1)%len(self.players)
                    self.say(f"{current_player.get_name()} folds.")
                    confirm_needed = False
                    continue
                else:
                    current_bids[current_player_idx] += player_bid
            elif player_bid > call_amount:
                current_bids[current_player_idx] += player_bid
                self.prev_raise_idx = last_raise_idx
                last_raise_idx = current_player_idx
                current_raise = current_bids[current_player_idx]
                self.say(f"{current_player.get_name()} raises. bid is now {current_raise}")
            else:
                current_bids[current_player_idx] += player_bid
                if player_bid > 0:
                    self.say(f"{current_player.get_name()} calls.")
                else:
                    self.say(f"{current_player.get_name()} checks.")
                    confirm_needed = False
            if current_player.worth() == 0:
                player_max_earnings[current_player_idx] = pot + (current_bids[current_player_idx])*self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings)
                self.say(f"{current_player.get_name()} goes all in.\nTheir maximum earning potential is {player_max_earnings[current_player_idx]}")
            if (not isinstance(current_player, human)) and current_raise > 0 and self.MODE == mode.HYBRID_PLAY and confirm_needed:
                utils.confirm("")
            current_player_idx = (current_player_idx+1)%len(self.players)
            # if self.v: print(f"\nround {roundabout}:")
            # if self.v: print(f"players: {[player.get_name() for player in self.players]}")
            # if self.v: print(f"current bids: {current_bids}")
            # if self.v: print(f"current_raise: {current_raise}")
            # if self.v: print(f"last raise index: {last_raise_idx}")
            # if self.v: print(f"current idx: {current_player_idx}")
            # if self.v: print(f"folded players: {folded_players}")
            # if self.v: print(f"player_max_earnings: {player_max_earnings}\n")
            roundabout += 1
            if self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings) <= 1:
                break
        
        if self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings) <= 1:
            pot = sum(current_bids)
            return pot, folded_players, player_max_earnings, last_raise_idx

        # big blind needs an extra turn
        confirm_needed = True
        if self.v: print(f"{self.players[big_blind_idx].get_name()}'s turn")
        big_blind_auth = self.auths[big_blind_idx]
        big_blind_player = self.players[big_blind_idx]
        call_amount = current_raise - current_bids[big_blind_idx]
        others_worth = [player.worth() for player in self.players]
        player_bid = big_blind_player.decide(auth=big_blind_auth, call_amount=call_amount, tabled_cards=[], others_worth=others_worth, pot=0, player_bids=current_bids, player_turn=current_player_idx, player_names=[player.get_name() for player in self.players], folded_players=folded_players, last_raise_idx=last_raise_idx, prev_raise_idx=self.prev_raise_idx)
        if player_bid < call_amount:
            if big_blind_player.worth() > 0:
                folded_players[big_blind_idx] = True
                self.say(f"{big_blind_player.get_name()} folds.")
                confirm_needed = False
            else:
                current_bids[big_blind_idx] += player_bid
        elif player_bid > call_amount:
            current_bids[big_blind_idx] += player_bid
            self.prev_raise_idx = last_raise_idx
            last_raise_idx = big_blind_idx
            current_raise = current_bids[big_blind_idx]
            self.say(f"{big_blind_player.get_name()} raises. bid is now {current_raise}")
        else:
            current_bids[big_blind_idx] += player_bid
            if player_bid > 0:
                self.say(f"{big_blind_player.get_name()} calls")
            else:
                self.say(f"{big_blind_player.get_name()} checks")
                confirm_needed = False
        if big_blind_player.worth() == 0:
            player_max_earnings[big_blind_idx] = pot + (current_bids[big_blind_idx])*self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings)
            self.say(f"{big_blind_player.get_name()} goes all in.\nTheir maximum earning potential is {player_max_earnings[current_player_idx]}")
        if (not isinstance(big_blind_player, human)) and current_raise > 0 and self.MODE == mode.HYBRID_PLAY and confirm_needed:
            utils.confirm("")
        
        current_player_idx = (big_blind_idx+1)%len(self.players)
        # if self.v: print(f"current_raise: {current_raise}")
        # if self.v: print(f"big blind: {self.big_blind}")

        # if self.v: print(f"current_player_idx: {current_player_idx}")
        # if self.v: print(f"last raise idx: {last_raise_idx}")
        # utils.confirm("")


        if current_raise > self.big_blind:
            while current_player_idx != last_raise_idx:
                confirm_needed = True
                # if self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings) <= 1 and current_bids[current_player_idx] == current_raise:
                #     break
                if folded_players[current_player_idx] or player_max_earnings[current_player_idx]<np.inf:
                    # the player has either folded, or has gone all in. In either case, we continue to the next player
                    if self.v: print(f"{self.players[current_player_idx].get_name()} cannot bet")
                    current_player_idx = (current_player_idx+1)%len(self.players)
                    continue
                if self.v: print(f"\n{self.players[current_player_idx].get_name()}'s turn")
                current_auth = self.auths[current_player_idx]
                current_player = self.players[current_player_idx]
                call_amount = current_raise - current_bids[current_player_idx]
                others_worth = [player.worth() for player in self.players]
                player_bid = current_player.decide(auth=current_auth, call_amount=call_amount, tabled_cards=[], others_worth=others_worth, pot=0, player_bids=current_bids, player_turn=current_player_idx, player_names=[player.get_name() for player in self.players], folded_players=folded_players, last_raise_idx=last_raise_idx, prev_raise_idx=self.prev_raise_idx)
                
                if player_bid < call_amount:
                    if current_player.worth() > 0:
                        folded_players[current_player_idx] = True
                        current_player_idx = (current_player_idx+1)%len(self.players)
                        self.say(f"{current_player.get_name()} folds.")
                        confirm_needed = False
                        continue
                    else:
                        current_bids[current_player_idx] += player_bid
                elif player_bid > call_amount:
                    current_bids[current_player_idx] += player_bid
                    self.prev_raise_idx = last_raise_idx
                    last_raise_idx = current_player_idx
                    current_raise = current_bids[current_player_idx]
                    self.say(f"{current_player.get_name()} raises. bid is now {current_raise}")
                else:
                    current_bids[current_player_idx] += player_bid
                    if player_bid > 0:
                        self.say(f"{current_player.get_name()} calls.")
                    else:
                        self.say(f"{current_player.get_name()} checks.")
                        confirm_needed = False
                if current_player.worth() == 0:
                    player_max_earnings[current_player_idx] = pot + (current_bids[current_player_idx])*self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings)
                    self.say(f"{current_player.get_name()} goes all in.\nTheir maximum earning potential is {player_max_earnings[current_player_idx]}")
                if (not isinstance(current_player, human)) and current_raise > 0 and self.MODE == mode.HYBRID_PLAY and confirm_needed:
                    utils.confirm("")
                current_player_idx = (current_player_idx+1)%len(self.players)
                # if self.v: print(f"\nround {roundabout}:")
                # if self.v: print(f"players: {[player.get_name() for player in self.players]}")
                # if self.v: print(f"current bids: {current_bids}")
                # if self.v: print(f"current_raise: {current_raise}")
                # if self.v: print(f"last raise index: {last_raise_idx}")
                # if self.v: print(f"current idx: {current_player_idx}")
                # if self.v: print(f"folded players: {folded_players}")
                # if self.v: print(f"player_max_earnings: {player_max_earnings}\n")
                roundabout += 1
            
        
        pot = sum(current_bids)
        return pot, folded_players, player_max_earnings, last_raise_idx
  
    def post_flop_bet(self, pot, folded_players, player_max_earnings, tabled_cards, last_raise_idx, dealer_idx):
        current_raise = 0
        current_bids = [0]*len(self.players)
        last_raise_idx = last_raise_idx%len(self.players)
        dealer_idx = dealer_idx%len(self.players)
        current_player_idx = (dealer_idx+1)%len(self.players)
        stop_idx = current_player_idx
        roundabout = 0
        do = True
        while (current_player_idx != stop_idx or do):
            # if self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings) <= 1 and current_bids[current_player_idx] == current_raise:
            #     break
            do = False
            if folded_players[current_player_idx] or player_max_earnings[current_player_idx] < np.inf:
                # the player has either folded, or has gone all in. In either case, we continue to the next player
                if self.v: print(f"{self.players[current_player_idx].get_name()} cannot bet. skipping")
                current_player_idx = (current_player_idx+1)%len(self.players)

                continue
            if self.v: print(f"\n{self.players[current_player_idx].get_name()}'s turn")

            current_auth = self.auths[current_player_idx]
            current_player = self.players[current_player_idx]
            call_amount = current_raise - current_bids[current_player_idx]
            others_worth = [player.worth() for player in self.players]
            player_bid = current_player.decide(auth=current_auth, call_amount=call_amount, tabled_cards=tabled_cards, others_worth=others_worth, pot=pot, player_bids=current_bids, player_turn=current_player_idx, player_names=[player.get_name() for player in self.players], folded_players=folded_players, last_raise_idx=last_raise_idx, prev_raise_idx=self.prev_raise_idx)
            
            if player_bid < call_amount:
                if current_player.worth() > 0:
                    folded_players[current_player_idx] = True
                    current_player_idx = (current_player_idx+1)%len(self.players)
                    self.say(f"{current_player.get_name()} folds.")
                    continue
                else:
                    current_bids[current_player_idx] += player_bid
            elif player_bid > call_amount:
                current_bids[current_player_idx] += player_bid
                self.prev_raise_idx = last_raise_idx
                last_raise_idx = current_player_idx
                stop_idx = last_raise_idx
                current_raise = current_bids[current_player_idx]
                self.say(f"{current_player.get_name()} raises. bid is now {current_raise}")
            else:
                current_bids[current_player_idx] += player_bid
                if player_bid > 0:
                    self.say(f"{current_player.get_name()} calls.")
                else:
                    self.say(f"{current_player.get_name()} checks.")
            if current_player.worth() == 0:
                player_max_earnings[current_player_idx] = pot + (current_bids[current_player_idx])*self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings)
                self.say(f"{current_player.get_name()} goes all in.\nTheir maximum earning potential is {player_max_earnings[current_player_idx]}")
            if (not isinstance(current_player, human)) and current_raise > 0 and self.MODE == mode.HYBRID_PLAY:
                utils.confirm("")
            current_player_idx = (current_player_idx+1)%len(self.players)
            # if self.v: print(f"\nround {roundabout}:")
            # if self.v: print(f"players: {[player.get_name() for player in self.players]}")
            # if self.v: print(f"current bids: {current_bids}")
            # if self.v: print(f"current_raise: {current_raise}")
            # if self.v: print(f"last raise index: {last_raise_idx}")
            # if self.v: print(f"current idx: {current_player_idx}")
            # if self.v: print(f"folded players: {folded_players}")
            # if self.v: print(f"player_max_earnings: {player_max_earnings}\n")
            roundabout += 1
            
        pot += sum(current_bids)
        return pot, folded_players, player_max_earnings, last_raise_idx

    def distribute_wealth(self, pot, folded_players, player_max_earnings, tabled_cards):
        if sum(folded_players) == len(self.players) - 1:
            winner_idx = folded_players.index(False)
            winner = self.players[winner_idx]
            auth = self.auths[winner_idx]
            confirm(f"{winner.get_name()} wins {pot} moneys") if self.MODE == mode.HYBRID_PLAY else self.say(f"{winner.get_name()} wins {pot} moneys")
            winner.add_money(auth,pot)
            return
        player_best_hands = [None]*len(self.players)
        player_hands = [None]*len(self.players)
        player_cards = [None]*len(self.players)
        for idx in range(len(self.players)):
            if folded_players[idx]:
                player_best_hands[idx] = (0,0,0,0,0,0)
                continue
            player = self.players[idx]
            auth = self.auths[idx]
            if self.v: print(tabled_cards)
            confirm(f"{player.get_name()} reveals hand") if self.MODE == mode.HYBRID_PLAY else self.say(f"{player.get_name()} reveals hand")
            hand = player.reveal_hand(auth)
            player_cards[idx] = hand
            cardnames = utils.card_list_to_card_names([utils.tuple_to_str(c) for c in hand])
            self.say(f"{player.get_name()} reveals the {cardnames[0]} and the {cardnames[1]}")
            hand = hand + tabled_cards
            player_hands[idx] = hand
            player_best_hands[idx] = utils.calc_best_hand(hand)
        winning_order = sorted(range(len(player_best_hands)), key=player_best_hands.__getitem__)[::-1]
        if self.v: print(f"player_best_hands_arr: {np.array(player_best_hands)}")
        if self.v: print(f"winning_order: {winning_order}")

        pool = ThreadPool()
        others_worth = [player.worth() for player in self.players]
        player_names = [player.get_name() for player in self.players]

        # if self.v: print([player.get_name() for player in self.players])
        # if self.v: print([auth for auth in self.auths])

        acync_results = [pool.apply_async(player.get_results, args=(self.auths[i], tabled_cards, others_worth, pot, player_names, player_cards)) for i,player in enumerate(self.players)]

        
        player_messages = []
        for i in range(len(player_best_hands)):
            #TODO: say out load all players hands
            player = self.players[i]
            if folded_players[i]:
                if self.v: print(f"{player.get_name()} folded")
                player_messages.append(f"{player.get_name()} folded")
                continue
            hand = player_best_hands[i]
            cards = player_hands[i]
            handname = utils.num_to_hand[hand[0]]
            cardnames = utils.card_list_to_card_names(utils.interpret_hand(hand,cards))
            player_messages.append(f"{player.get_name()} has {handname} with {cardnames}")
            if self.v: print(player_messages[-1])
        if self.v: print()
        
        starting_winning_indexer = 0
        while pot > 0:
            tie_index = starting_winning_indexer+1
            while tie_index < len(player_best_hands):
                if player_best_hands[winning_order[starting_winning_indexer]] == player_best_hands[winning_order[tie_index]]:
                    tie_index += 1
                else:
                    break
            winning_player_indexes = winning_order[starting_winning_indexer:tie_index]
            if len(winning_player_indexes) == 1:
                if player_max_earnings[winning_player_indexes[0]] < pot:
                    max_earning = player_max_earnings[winning_player_indexes[0]]
                    self.say(player_messages[winning_player_indexes[0]])
                    confirm(f"{self.players[winning_player_indexes[0]].get_name()} wins {max_earning} moneys") if self.MODE == mode.HYBRID_PLAY else self.say(f"{self.players[winning_player_indexes[0]].get_name()} wins {max_earning} moneys")
                    auth = self.auths[winning_player_indexes[0]]
                    self.players[winning_player_indexes[0]].add_money(auth, max_earning)
                    pot -= max_earning
                else:
                    self.say(player_messages[winning_player_indexes[0]])
                    confirm(f"{self.players[winning_player_indexes[0]].get_name()} wins the pot of {pot} moneys") if self.MODE == mode.HYBRID_PLAY else self.say(f"{self.players[winning_player_indexes[0]].get_name()} wins the pot of {pot} moneys")
                    auth = self.auths[winning_player_indexes[0]]
                    self.players[winning_player_indexes[0]].add_money(auth, pot)
                    pot = 0
                pass
            else:
                self.say(f"we have a tie between {[self.players[winning_player_indexes[i]].get_name() for i in range(len(winning_player_indexes))]}")
                pot_divided = pot//len(winning_player_indexes)
                remainder = pot%len(winning_player_indexes)
                player_winnings = [pot_divided]*len(winning_player_indexes)
                while remainder > 0:
                    self.say(f"{pot} cannot be divided equally among {len(winning_player_indexes)} players.")
                    remainder_doling_starting_index = np.random.randint(len(winning_player_indexes))
                    self.say(f"remainder of {remainder} will be doled out starting with {self.players[winning_player_indexes[remainder_doling_starting_index]].get_name()}.")
                    while remainder > 0:
                        player_winnings[remainder_doling_starting_index] += 1
                        remainder -= 1
                        remainder_doling_starting_index = (remainder_doling_starting_index+1)%len(player_winnings)
                    # remainder should be reset to 0 now
                    num_players_at_max = 0
                    for i,winner_idx in enumerate(winning_player_indexes):
                        player = self.players[winner_idx]
                        max_earnings = player_max_earnings[winner_idx]
                        if max_earnings < np.inf:
                            self.say(f"{player.get_name()} can only win {max_earnings}. the rest will be redistributed")
                        if max_earnings < player_winnings[i]:
                            remainder += player_winnings[i] - max_earnings
                            player_winnings[i] = max_earnings
                            num_players_at_max += 1
                    if num_players_at_max == len(winning_player_indexes):
                        # every player has a cap, and has reached that cap. we need to move on
                        break
                for i,idx in enumerate(winning_player_indexes):
                    auth = self.auths[idx]
                    player = self.players[idx]
                    winnings = player_winnings[i]
                    self.say(player_messages[winning_player_indexes[i]])
                    confirm(f"{player.get_name()} wins {winnings} moneys") if self.MODE == mode.HYBRID_PLAY else self.say(f"{player.get_name()} wins {winnings} moneys")
                    player.add_money(auth, winnings)
                    pot -= winnings
            starting_winning_indexer = tie_index
        
        for i,res in enumerate(acync_results):
            if not res.ready():
                self.say(f'waiting on {self.players[i].get_name()}')
            r = res.get()
            if self.v: print(r)
        
        pool.close()
        pool.join()



    def check_lost_players(self, dealer_idx):
        need_recheck = True
        while need_recheck:
            need_recheck = False
            for i,player in enumerate(self.players):
                if player.worth() == 0:
                    need_recheck = True
                    loser = self.players.pop(i)
                    self.auths.pop(i)
                    self.say(f"{loser.get_name()} has lost")
                    need_recheck = True
                    if i <= dealer_idx:
                        dealer_idx -= 1
                    break
        return dealer_idx+1

    def play_game(self):
        """
            in hybrid game, a dealer deals cards out and each AI opponent's cards are input.
            players cards are not dealt by the computer
        """
        # first_round = True
        dealer_idx = 0
        while len(self.players) > 1:

            for player in self.players:
                self.say(f"{player.get_name()} has {player.worth()} moneys")

            if self.v: print()
            dealer_name = self.players[dealer_idx].get_name()
            self.say(f"{dealer_name} deals.")
            if self.MODE == mode.HYBRID_PLAY: utils.confirm(f"deal.")
            remaining_deck, str_remaining, strranks, strsuits, num_to_hand = utils.create_deck()
            tabled_cards = []


            for i,player in enumerate(self.players):
                if not isinstance(player, human):
                    cards = []
                    if self.MODE == mode.HYBRID_PLAY:
                        if self.first_round:
                            say(f"{player.get_name()} is an AI")
                            say(f"enter their cards: ")
                            
                        else:
                            say(f"enter {player.get_name()}'s cards: ")
                        while len(cards) < 2:
                            if self.v: print(f"current cards: {cards}")
                            utils.add_to_list(cards, max_size=2)
                    else:
                        utils.computer_add(cards, str_remaining=str_remaining, remaining_cards=remaining_deck, max_size=2)
                    player.new_hand(self.auths[i], cards)
            self.first_round = False

            # TODO: if everybody but one folded, end the round before moving to the next phase

            pot, folded_players, player_max_earnings, last_raise_idx = self.pre_flop_bet(dealer_idx)
            self.say(f"pot is now {pot}")

            if sum(folded_players) >= len(self.players)-1:
                self.say("all players have folded. distributing wealth")
                self.distribute_wealth(pot, folded_players, player_max_earnings, tabled_cards)
                dealer_idx = self.check_lost_players(dealer_idx)%len(self.players)
                continue
            while len(tabled_cards) < 3:
                if self.MODE == mode.HYBRID_PLAY:
                    if self.v: print(f"current tabled cards: {[utils.tuple_to_str(c) for c in tabled_cards]}")
                    say(f"{self.players[dealer_idx].get_name()}, deal the flop. Enter cards: ")
                    utils.add_to_list(tabled_cards, max_size=3)
                else:
                    self.say(f"{self.players[dealer_idx].get_name()} deals the flop.")
                    utils.computer_add(tabled_cards, str_remaining=str_remaining, remaining_cards=remaining_deck, max_size=3)
            if self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings) > 1:
                pot, folded_players, player_max_earnings, last_raise_idx = self.post_flop_bet(pot, folded_players, player_max_earnings, tabled_cards, last_raise_idx, dealer_idx)
                self.say(f"pot is now {pot}")
            if sum(folded_players) >= len(self.players)-1:
                self.say("all players have folded. distributing wealth")
                self.distribute_wealth(pot, folded_players, player_max_earnings, tabled_cards)
                dealer_idx = self.check_lost_players(dealer_idx)%len(self.players)
                continue
            while len(tabled_cards) < 4:
                if self.MODE == mode.HYBRID_PLAY:
                    if self.v: print(f"current tabled cards: {[utils.tuple_to_str(c) for c in tabled_cards]}")
                    say(f"{self.players[dealer_idx].get_name()}, deal the turn. Enter card: ")
                    utils.add_to_list(tabled_cards, max_size=4)
                else:
                    self.say(f"{self.players[dealer_idx].get_name()} deals the turn.")
                    utils.computer_add(tabled_cards, str_remaining=str_remaining, remaining_cards=remaining_deck, max_size=4)
            if self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings) > 1:
                pot, folded_players, player_max_earnings, last_raise_idx = self.post_flop_bet(pot, folded_players, player_max_earnings, tabled_cards, last_raise_idx, dealer_idx)
                self.say(f"pot is now {pot}")
            if sum(folded_players) >= len(self.players)-1:
                self.say("all players have folded. distributing wealth")
                self.distribute_wealth(pot, folded_players, player_max_earnings, tabled_cards)
                dealer_idx = self.check_lost_players(dealer_idx)%len(self.players)
                continue
            while len(tabled_cards) < 5:
                if self.MODE == mode.HYBRID_PLAY:
                    if self.v: print(f"current tabled cards: {[utils.tuple_to_str(c) for c in tabled_cards]}")
                    say(f"{self.players[dealer_idx].get_name()}, deal the river. Enter card: ")
                    utils.add_to_list(tabled_cards, max_size=5)
                else:
                    self.say(f"{self.players[dealer_idx].get_name()} deals the river.")
                    utils.computer_add(tabled_cards, str_remaining=str_remaining, remaining_cards=remaining_deck, max_size=5)
            if self.num_betting_players(folded_players=folded_players, player_max_earnings=player_max_earnings) > 1:
                pot, folded_players, player_max_earnings, _ = self.post_flop_bet(pot, folded_players, player_max_earnings, tabled_cards, last_raise_idx, dealer_idx)
                self.say(f"pot is now {pot}")
            if sum(folded_players) >= len(self.players)-1:
                self.say("all players have folded. distributing wealth")
            self.distribute_wealth(pot, folded_players, player_max_earnings, tabled_cards)
            dealer_idx = self.check_lost_players(dealer_idx)%len(self.players)
        winner = self.players[0]
        self.say(f"{winner.get_name()} wins!")
    
    def start_game(self):
        game_on = True
        while game_on:
            os.system("clear")
            try:
                self.play_game()
                game_on = False
            except KeyboardInterrupt as e:
                found_valid_input = False
                while not found_valid_input:
                    os.system("clear")
                    print("You have entered the edit menu.")
                    print("unfortunately, we cannot fix player's cards mid-round,")
                    print("but we can edit their money post-round.")
                    print("Enter each player's money as integers")
                    print("below, separated by spaces.")
                    print("any invalid input will reprompt this message.")
                    print("CTRL-C will quit the program entirely.")
                    print(f"player order: {[player.get_name() for player in self.players]}")
                    moneys = input("Enter money amounts: ")
                    try:
                        amounts = [int(a) for a in moneys.strip().split()]
                        assert len(amounts) == len(self.players)
                        for i,player in enumerate(self.players):
                            player.money = amounts[i]
                    except:
                        continue
                    print("new player moneys:")
                    [print(player.get_name(),player.worth()) for player in self.players]
                    temp = input("Press enter to confirm amounts: ")
                    found_valid_input = True


if __name__ == "__main__":
    os.system("clear")

    parser = argparse.ArgumentParser()
    parser.add_argument("num_players",help="the number of players")
    parser.add_argument("--names",nargs="*",help="player names. if not enough are specified, will prompt for more")
    parser.add_argument("--classes",nargs="*", help="the corresponding player classes. if not enough are specified, or if a player subclass cannot be found with the specified name, will prompt for more")
    parser.add_argument("--force-speak",action="store_true",default=False)
    parser.add_argument("--small-blind",default="1")
    parser.add_argument("--big-blind",default="2")
    parser.add_argument("--starting-money",default="100")
    parser.add_argument(f"--force-hybrid",action="store_true",default=False)

    args = parser.parse_args()
    num_players = int(args.num_players)
    small_blind = int(args.small_blind)
    big_blind = int(args.big_blind)
    starting_money = int(args.starting_money)

    def get_player_subclasses():
        def get_subclasses(cls):
            for c in cls.__subclasses__():
                yield c
                for subclass in get_subclasses(c):
                    yield subclass
        return [player] + [subclass for subclass in get_subclasses(player)]
    
    all_players = [] # list of the player names along with their constructors

    if args.names is not None and args.classes is not None:
        for i in range(min(len(args.names),len(args.classes))):
            current_name = args.names[i]
            current_class = args.classes[i]
            for subclass in get_player_subclasses():
                if current_class == subclass.__name__:
                    all_players.append((subclass, current_name))


    os.system("clear")
    while len(all_players) < num_players:
        print(f"Current players ({len(all_players)}/{num_players}):")
        [print(f"{name}: {subclass}") for (subclass,name) in all_players]
        print("\nknown subclasses:")
        [print(subclass) for subclass in get_player_subclasses()]

        current_class = input("\nenter desired subclass: ")

        found_subclass = False
        for subclass in get_player_subclasses():
            if current_class == subclass.__name__:
                current_name = input("enter player name: ")
                all_players.append((subclass, current_name))
                found_subclass = True
                break
        os.system("clear")
        if not found_subclass:
            print(f"failed to find subclass {current_class}. try again")
            print()
    sayfunc = None
    if args.force_speak or args.force_hybrid:
        sayfunc = utils.say
    else:
        has_human = False
        for subclass,_ in all_players:
            if subclass.__name__ == "human":
                has_human = True
                break
        if has_human:
            sayfunc = utils.say
        else:
            sayfunc = print
    player_constructors = [subclass.constructor for subclass,_ in all_players]
    player_names = [name for _,name in all_players]
    
    t = table(player_constructors=player_constructors, player_names=player_names,starting_money=starting_money, small_blind=small_blind, big_blind=big_blind, say=sayfunc)
    if args.force_hybrid:
        t.MODE = mode.HYBRID_PLAY
    try:
        t.start_game()
    except KeyboardInterrupt as e:
        os.system("clear")
        fancy_out("process terminated", sleep_time=.03)
        time.sleep(0.3)
        os.system("clear")

