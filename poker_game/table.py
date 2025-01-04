import numpy as np
import time
import utils

from players import *
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
    def __init__(self, player_constructors:list, player_names:list, starting_money:int, small_blind:int=1, big_blind:int=None):
        assert len(player_constructors) == len(player_names)
        if big_blind is None:
            big_blind = small_blind*2
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.players = []
        self.auths = []
        self.MODE = mode.COMPUTER_ONLY
        for i,constructor in enumerate(player_constructors):
            print(i,player_names[i])
            auth = np.random.randint(1000000)
            self.auths.append(auth)
            new_player = constructor(player_names[i],auth)
            new_player.add_money(auth, starting_money)
            if isinstance(new_player, human):
                self.MODE = mode.HYBRID_PLAY
            self.players.append(new_player)
    
    def play_game(self):
        if self.MODE == mode.HYBRID_PLAY:
            self.__hybrid_game()
        elif self.MODE == mode.COMPUTER_ONLY:
            self.__computer_game()
    
    def initiate_blinds(self, dealer_idx):
        current_bids = [0]*len(self.players)
        player_max_earnings = [np.inf]*len(self.players)

        small_blind_index = (dealer_idx+1)%len(self.players)
        big_blind_index = (dealer_idx+2)%len(self.players)

        small_blind_auth = self.auths[small_blind_index]
        big_blind_auth = self.auths[big_blind_index]

        small_blind_player = self.players[small_blind_index]
        big_blind_player = self.players[big_blind_index]

        current_bids[small_blind_index] = small_blind_player.blind(small_blind_auth, self.small_blind)
        if current_bids[small_blind_index] < self.small_blind:
            player_max_earnings[small_blind_index] = current_bids[small_blind_index]*len(self.players)

        current_bids[big_blind_index] = big_blind_player.blind(big_blind_auth, self.big_blind)
        if current_bids[big_blind_index] < self.big_blind:
            player_max_earnings[big_blind_index] = current_bids[big_blind_index]*len(self.players)

        return current_bids, player_max_earnings
    
    def pre_flop_bet(self, dealer_idx):
        current_bids,player_max_earnings = self.initiate_blinds(dealer_idx)
        current_raise = self.big_blind
        last_raise_idx = (dealer_idx+2)%len(self.players)
        current_player_idx = (dealer_idx+3)%len(self.players)
        folded_players = [False]*len(self.players)
        pot = 0
        roundabout = 0
        while current_player_idx != last_raise_idx:
            if folded_players[current_player_idx] or player_max_earnings[current_player_idx]<np.inf:
                # the player has either folded, or has gone all in. In either case, we continue to the next player
                current_player_idx = (current_player_idx+1)%len(self.players)
                continue
            current_auth = self.auths[current_player_idx]
            current_player = self.players[current_player_idx]
            call_amount = current_raise - current_bids[current_player_idx]
            others_worth = [player.worth() for player in self.players]
            player_bid = current_player.decide(auth=current_auth, call_amount=call_amount, tabled_cards=[], others_worth=others_worth, pot=0, player_bids=current_bids, player_turn=current_player_idx)
            if player_bid < call_amount:
                if current_player.worth() > 0:
                    folded_players[current_player_idx] = True
                    current_player_idx = (current_player_idx+1)%len(self.players)
                    continue
                else:
                    current_bids[current_player_idx] += player_bid
                    player_max_earnings[current_player_idx] = pot + (current_bids[current_player_idx])*len(self.players)
            elif player_bid > call_amount:
                current_bids[current_player_idx] += player_bid
                last_raise_idx = current_player_idx
                current_raise = current_bids[current_player_idx]
            else:
                current_bids[current_player_idx] += player_bid
            current_player_idx = (current_player_idx+1)%len(self.players)
            print(f"\nround {roundabout}:")
            print(f"players: {[player.get_name() for player in self.players]}")
            print(f"current bids: {current_bids}")
            print(f"current_raise: {current_raise}")
            print(f"last raise index: {last_raise_idx}")
            print(f"current idx: {current_player_idx}")
            print(f"folded players: {folded_players}")
            print(f"player_max_earnings: {player_max_earnings}\n")
            roundabout += 1


        
        pot = sum(current_bids)
        return pot, folded_players, player_max_earnings
  
    def post_flop_bet(self, dealer_idx, pot, folded_players, player_max_earnings, tabled_cards):
        current_raise = 0
        current_bids = [0]*len(self.players)
        last_raise_idx = dealer_idx
        current_player_idx = (dealer_idx+1)%len(self.players)
        roundabout = 0
        while current_player_idx != last_raise_idx:
            if folded_players[current_player_idx] or player_max_earnings[current_player_idx] < np.inf:
                # the player has either folded, or has gone all in. In either case, we continue to the next player
                current_player_idx = (current_player_idx+1)%len(self.players)
                continue

            current_auth = self.auths[current_player_idx]
            current_player = self.players[current_player_idx]
            call_amount = current_raise - current_bids[current_player_idx]
            others_worth = [player.worth() for player in self.players]
            player_bid = current_player.decide(auth=current_auth, call_amount=call_amount, tabled_cards=[], others_worth=others_worth, pot=0, player_bids=current_bids, player_turn=current_player_idx)

            if player_bid < call_amount:
                if current_player.worth() > 0:
                    folded_players[current_player_idx] = True
                    current_player_idx = (current_player_idx+1)%len(self.players)
                    continue
                else:
                    current_bids[current_player_idx] += player_bid
                    player_max_earnings[current_player_idx] = pot + (current_bids[current_player_idx])*len(self.players)
            elif player_bid > call_amount:
                current_bids[current_player_idx] += player_bid
                last_raise_idx = current_player_idx
                current_raise = current_bids[current_player_idx]
            else:
                current_bids[current_player_idx] += player_bid

            current_player_idx = (current_player_idx+1)%len(self.players)
            print(f"\nround {roundabout}:")
            print(f"players: {[player.get_name() for player in self.players]}")
            print(f"current bids: {current_bids}")
            print(f"current_raise: {current_raise}")
            print(f"last raise index: {last_raise_idx}")
            print(f"current idx: {current_player_idx}")
            print(f"folded players: {folded_players}")
            print(f"player_max_earnings: {player_max_earnings}\n")
            roundabout += 1
        pot = sum(current_bids)
        return pot, folded_players, player_max_earnings

    def __hybrid_game(self):
        """
            in hybrid game, a dealer deals cards out and each AI opponent's cards are input.
            players cards are not dealt by the computer
        """
        dealer_idx = 0
        while len(self.players) > 1:
            remaining_deck, str_remaining, strranks, strsuits, num_to_hand = utils.create_deck()

            def distribute_wealth():
                player_hands = [None]*len(self.players)
                for idx in range(len(self.players)):
                    if folded_players[idx]:
                        continue
                    player = self.players[idx]
                    auth = self.auths[idx]
                    player_hands[idx] = player.reveal_hand(auth)

            for i,player in enumerate(self.players):
                if not isinstance(player,human):
                    cards = []
                    print(f"enter {player.get_name()}'s cards: ")
                    utils.add_to_list(cards, str_remaining, remaining_deck, max_size=2)
                    player.new_hand(self.auths[i], cards)


            # TODO: if everybody but one folded, end the round before moving to the next phase

            pot, folded_players, player_max_earnings = self.pre_flop_bet(dealer_idx)
            tabled_cards = []
            if sum(folded_players) >= len(self.players)-1:
                distribute_wealth()
                continue
            while len(tabled_cards) < 3:
                utils.add_to_list(tabled_cards, str_remaining, remaining_deck, max_size=3)
            pot, folded_players, player_max_earnings = self.post_flop_bet(dealer_idx, pot, folded_players, player_max_earnings, tabled_cards)
            if sum(folded_players) >= len(self.players)-1:
                distribute_wealth()
                continue
            while len(tabled_cards) < 4:
                utils.add_to_list(tabled_cards, str_remaining, remaining_deck, max_size=4)
            pot, folded_players, player_max_earnings = self.post_flop_bet(dealer_idx, pot, folded_players, player_max_earnings, tabled_cards)
            if sum(folded_players) >= len(self.players)-1:
                distribute_wealth()
                continue
            while len(tabled_cards) < 5:
                utils.add_to_list(tabled_cards, str_remaining, remaining_deck, max_size=5)
            pot, folded_players, player_max_earnings = self.post_flop_bet(dealer_idx, pot, folded_players, player_max_earnings, tabled_cards)
            distribute_wealth()
            




        pass

    def __computer_game(self):
        """
            in computer game, the computer deals all cards out and manages everything. it should play relatively quickly,
            as all decisions are made by computers
        """
        dealer_idx = 0
        while len(self.players) > 1:
            remaining_deck, str_remaining, strranks, strsuits, num_to_hand = utils.create_deck()

            for i,player in enumerate(self.players):
                if isinstance(player,human):
                    raise RuntimeError(f"{player.get_name()} is a human in a computer only game!")
                new_hand = []
                for i in range(2):
                    idx = np.random.randint(len(remaining_deck))
                    card = remaining_deck[idx]
                    cardstr = utils.tuple_to_str(card)
                    remaining_deck.remove(card)
                    str_remaining.remove(cardstr)
                    new_hand.append(card)
                player.new_hand(self.auths[i], new_hand)

                        

            pot, folded_players, player_max_earnings = self.pre_flop_bet(dealer_idx)
            tabled_cards = []
            while len(tabled_cards) < 3:
                idx = np.random.randint(len(remaining_deck))
                card = remaining_deck[idx]
                cardstr = utils.tuple_to_str(card)
                remaining_deck.remove(card)
                str_remaining.remove(cardstr)
                tabled_cards.append(card)
            
            pot, folded_players, player_max_earnings = self.post_flop_bet(dealer_idx, pot, folded_players, player_max_earnings, tabled_cards)
            while len(tabled_cards) < 4:
                idx = np.random.randint(len(remaining_deck))
                card = remaining_deck[idx]
                cardstr = utils.tuple_to_str(card)
                remaining_deck.remove(card)
                str_remaining.remove(cardstr)
                tabled_cards.append(card)

            pot, folded_players, player_max_earnings = self.post_flop_bet(dealer_idx, pot, folded_players, player_max_earnings, tabled_cards)
            while len(tabled_cards) < 5:
                idx = np.random.randint(len(remaining_deck))
                card = remaining_deck[idx]
                cardstr = utils.tuple_to_str(card)
                remaining_deck.remove(card)
                str_remaining.remove(cardstr)
                tabled_cards.append(card)

            pot, folded_players, player_max_earnings = self.post_flop_bet(dealer_idx, pot, folded_players, player_max_earnings, tabled_cards)

            player_hands = [None]*len(self.players)
            best_idx = 0
            best_hand = None
            for idx in range(len(self.players)):
                if folded_players[idx]:
                    continue
                player = self.players[idx]
                auth = self.auths[idx]
                hand = player.reveal_hand(auth) + tabled_cards
                hand_tuple = utils.calc_best_hand(hand)
                
                


        

if __name__ == "__main__":
    t = table(player_constructors=[human.constructor, human.constructor, human.constructor],player_names=["alice","bob","charlie"],starting_money=100)
    for p in t.players:
        print(p.get_name(),":",type(p))
    t.play_game()