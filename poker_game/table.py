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
            self.__hybrid_game()
    
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
        if current_bids[small_blind_index] < self.small_blind or small_blind_player.worth() == 0:
            player_max_earnings[small_blind_index] = current_bids[small_blind_index]*len(self.players)
            say(f"{small_blind_player.get_name()} is all in with {current_bids[small_blind_index]} for small blind.\
                Their max earning potential is now {player_max_earnings[small_blind_index]}")
        utils.confirm(f"{small_blind_player.get_name()} pays small blind of {current_bids[small_blind_index]}")

        current_bids[big_blind_index] = big_blind_player.blind(big_blind_auth, self.big_blind)
        if current_bids[big_blind_index] < self.big_blind or big_blind_player.worth() == 0:
            player_max_earnings[big_blind_index] = current_bids[big_blind_index]*len(self.players)
            say(f"{big_blind_player.get_name()} is all in with {current_bids[big_blind_index]} for big blind.\
                Their max earning potential is now {player_max_earnings[big_blind_index]}")
        utils.confirm(f"{big_blind_player.get_name()} pays big blind of {current_bids[big_blind_index]}")


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
                print(f"{self.players[current_player_idx].get_name()} cannot bet")
                current_player_idx = (current_player_idx+1)%len(self.players)
                continue
            print(f"{self.players[current_player_idx].get_name()}'s turn")
            current_auth = self.auths[current_player_idx]
            current_player = self.players[current_player_idx]
            call_amount = current_raise - current_bids[current_player_idx]
            others_worth = [player.worth() for player in self.players]
            player_bid = current_player.decide(auth=current_auth, call_amount=call_amount, tabled_cards=[], others_worth=others_worth, pot=0, player_bids=current_bids, player_turn=current_player_idx, player_names=[player.get_name() for player in self.players])
            if not isinstance(current_player, human):
                utils.confirm("")
            if player_bid < call_amount:
                if current_player.worth() > 0:
                    folded_players[current_player_idx] = True
                    current_player_idx = (current_player_idx+1)%len(self.players)
                    say(f"{current_player.get_name()} folds.")
                    continue
                else:
                    current_bids[current_player_idx] += player_bid
                    player_max_earnings[current_player_idx] = pot + (current_bids[current_player_idx])*len(self.players)
                    say(f"{current_player.get_name()} goes all in. their maximum earning potential is {player_max_earnings[current_player_idx]}")
            elif player_bid > call_amount:
                current_bids[current_player_idx] += player_bid
                last_raise_idx = current_player_idx
                current_raise = current_bids[current_player_idx]
                say(f"{current_player.get_name()} raises. bid is now {current_raise}")
                if current_player.worth() == 0:
                    player_max_earnings[current_player_idx] = pot + (current_bids[current_player_idx])*len(self.players)
                    say(f"{current_player.get_name()} goes all in. their maximum earning potential is {player_max_earnings[current_player_idx]}")
            else:
                current_bids[current_player_idx] += player_bid
                say(f"{current_player.get_name()} calls.")
                if current_player.worth() == 0:
                    player_max_earnings[current_player_idx] = pot + (current_bids[current_player_idx])*len(self.players)
                    say(f"{current_player.get_name()} goes all in. their maximum earning potential is {player_max_earnings[current_player_idx]}")
            
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
        current_player_idx = (dealer_idx+1)%len(self.players)
        last_raise_idx = current_player_idx
        roundabout = 0
        do = True
        while current_player_idx != last_raise_idx or do:
            do = False
            if folded_players[current_player_idx] or player_max_earnings[current_player_idx] < np.inf:
                # the player has either folded, or has gone all in. In either case, we continue to the next player
                print(f"{self.players[current_player_idx].get_name()} cannot bet. skipping")
                current_player_idx = (current_player_idx+1)%len(self.players)

                continue
            print(f"{self.players[current_player_idx].get_name()}'s turn")

            current_auth = self.auths[current_player_idx]
            current_player = self.players[current_player_idx]
            call_amount = current_raise - current_bids[current_player_idx]
            others_worth = [player.worth() for player in self.players]
            player_bid = current_player.decide(auth=current_auth, call_amount=call_amount, tabled_cards=tabled_cards, others_worth=others_worth, pot=0, player_bids=current_bids, player_turn=current_player_idx, player_names=[player.get_name() for player in self.players])
            if not isinstance(current_player, human):
                utils.confirm("")
            if player_bid < call_amount:
                if current_player.worth() > 0:
                    folded_players[current_player_idx] = True
                    current_player_idx = (current_player_idx+1)%len(self.players)
                    say(f"{current_player.get_name()} folds.")
                    continue
                else:
                    current_bids[current_player_idx] += player_bid
                    player_max_earnings[current_player_idx] = pot + (current_bids[current_player_idx])*len(self.players)
                    say(f"{current_player.get_name()} goes all in. their maximum earning potential is {player_max_earnings[current_player_idx]}")
            elif player_bid > call_amount:
                current_bids[current_player_idx] += player_bid
                last_raise_idx = current_player_idx
                current_raise = current_bids[current_player_idx]
                say(f"{current_player.get_name()} raises. bid is now {current_raise}")
            else:
                current_bids[current_player_idx] += player_bid
                say(f"{current_player.get_name()} calls.")

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
        pot += sum(current_bids)
        return pot, folded_players, player_max_earnings
    
    def distribute_wealth(self, pot, folded_players, player_max_earnings, tabled_cards):
        if sum(folded_players) == len(self.players) - 1:
            winner_idx = folded_players.index(False)
            winner = self.players[winner_idx]
            auth = self.auths[winner_idx]
            confirm(f"{winner.get_name()} wins {pot} moneys")
            winner.add_money(auth,pot)
            return
        player_hands = [None]*len(self.players)
        for idx in range(len(self.players)):
            if folded_players[idx]:
                player_hands[idx] = (0,0,0,0,0,0)
                continue
            player = self.players[idx]
            auth = self.auths[idx]
            print(tabled_cards)
            confirm(f"{player.get_name()} reveals hand")
            hand = player.reveal_hand(auth)
            print(hand)
            hand = hand + tabled_cards
            player_hands[idx] = utils.calc_best_hand(hand)
        winning_order = sorted(range(len(player_hands)), key=player_hands.__getitem__)[::-1]
        print(f"player_hands_arr: {np.array(player_hands)}")
        print(f"winning_order: {winning_order}")
        for i in range(len(player_hands)):
            #TODO: say out load all players hands
            pass
        starting_winning_indexer = 0
        while pot > 0:
            tie_index = starting_winning_indexer+1
            while tie_index < len(player_hands):
                if player_hands[winning_order[starting_winning_indexer]] == player_hands[winning_order[tie_index]]:
                    tie_index += 1
                else:
                    break
            winning_player_indexes = winning_order[starting_winning_indexer:tie_index]
            if len(winning_player_indexes) == 1:
                if player_max_earnings[winning_player_indexes[0]] < np.inf:
                    max_earning = player_max_earnings[winning_player_indexes[0]]
                    confirm(f"{self.players[winning_player_indexes[0]].get_name()} wins {max_earning} moneys")
                    auth = self.auths[winning_player_indexes[0]]
                    self.players[winning_player_indexes[0]].add_money(auth, max_earning)
                    pot -= max_earning
                else:
                    confirm(f"{self.players[winning_player_indexes[0]].get_name()} wins the pot of {pot} moneys")
                    auth = self.auths[winning_player_indexes[0]]
                    self.players[winning_player_indexes[0]].add_money(auth, pot)
                    pot = 0
                pass
            else:
                say(f"we have a tie between {[self.players[winning_player_indexes[i]].get_name() for i in range(len(winning_player_indexes))]}")
                pot_divided = pot//len(winning_player_indexes)
                remainder = pot%len(winning_player_indexes)
                player_winnings = [pot_divided]*len(winning_player_indexes)
                while remainder > 0:
                    # say(f"{pot} cannot be divided equally among {len(winning_player_indexes)} players.")
                    remainder_doling_starting_index = np.random.randint(len(winning_player_indexes))
                    say(f"remainder of {remainder} will be doled out starting with {self.players[winning_player_indexes[remainder_doling_starting_index]].get_name()}.")
                    while remainder > 0:
                        player_winnings[remainder_doling_starting_index] += 1
                        remainder -= 1
                        remainder_doling_starting_index = (remainder_doling_starting_index+1)%len(player_winnings)
                    # remainder should be reset to 0 now
                    num_players_at_max = 0
                    for i,winner_idx in enumerate(winning_player_indexes):
                        player = self.players[winner_idx]
                        max_earnings = player_max_earnings[winner_idx]
                        say(f"{player.get_name()} can only win {max_earnings}. the rest will be redistributed")
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
                    confirm(f"{player.get_name()} wins {winnings} moneys")
                    player.add_money(auth, winnings)
                    pot -= winnings
            starting_winning_indexer = tie_index

    def check_lost_players(self, dealer_idx):
        need_recheck = True
        while need_recheck:
            need_recheck = False
            for i,player in enumerate(self.players):
                if player.worth() == 0:
                    need_recheck = True
                    loser = self.players.pop(i)
                    self.auths.pop(i)
                    say(f"{loser.get_name()} has lost")
                    need_recheck = True
                    if i <= dealer_idx:
                        dealer_idx -= 1
                    break
        return dealer_idx+1


    def __hybrid_game(self):
        """
            in hybrid game, a dealer deals cards out and each AI opponent's cards are input.
            players cards are not dealt by the computer
        """
        dealer_idx = 0
        while len(self.players) > 1:

            for player in self.players:
                say(f"{player.get_name()} has {player.worth()} moneys")

            print()
            dealer_name = self.players[dealer_idx].get_name()
            utils.say(f"{dealer_name}'s turn to deal.")
            utils.confirm(f"deal.")
            remaining_deck, str_remaining, strranks, strsuits, num_to_hand = utils.create_deck()
            tabled_cards = []


            for i,player in enumerate(self.players):
                if not isinstance(player,human):
                    cards = []
                    say(f"{player.get_name()} is an AI. enter their cards: ")
                    while len(cards) < 2:
                        utils.add_to_list(cards, str_remaining, remaining_deck, max_size=2)
                    player.new_hand(self.auths[i], cards)


            # TODO: if everybody but one folded, end the round before moving to the next phase

            pot, folded_players, player_max_earnings = self.pre_flop_bet(dealer_idx)
            say(f"pot is now {pot}")

            if sum(folded_players) >= len(self.players)-1:
                say("all players have folded. distributing wealth")
                self.distribute_wealth(pot, folded_players, player_max_earnings, tabled_cards)
                dealer_idx = self.check_lost_players(dealer_idx)%len(self.players)
                continue
            while len(tabled_cards) < 3:
                say(f"{self.players[dealer_idx].get_name()}, deal the flop. Enter cards: ")
                utils.add_to_list(tabled_cards, str_remaining, remaining_deck, max_size=3)
            pot, folded_players, player_max_earnings = self.post_flop_bet(dealer_idx, pot, folded_players, player_max_earnings, tabled_cards)
            say(f"pot is now {pot}")
            if sum(folded_players) >= len(self.players)-1:
                say("all players have folded. distributing wealth")
                self.distribute_wealth(pot, folded_players, player_max_earnings, tabled_cards)
                dealer_idx = self.check_lost_players(dealer_idx)%len(self.players)
                continue
            while len(tabled_cards) < 4:
                say(f"{self.players[dealer_idx].get_name()}, deal the turn. Enter card: ")
                utils.add_to_list(tabled_cards, str_remaining, remaining_deck, max_size=4)
            pot, folded_players, player_max_earnings = self.post_flop_bet(dealer_idx, pot, folded_players, player_max_earnings, tabled_cards)
            say(f"pot is now {pot}")
            if sum(folded_players) >= len(self.players)-1:
                say("all players have folded. distributing wealth")
                self.distribute_wealth(pot, folded_players, player_max_earnings, tabled_cards)
                dealer_idx = self.check_lost_players(dealer_idx)%len(self.players)
                continue
            while len(tabled_cards) < 5:
                say(f"{self.players[dealer_idx].get_name()}, deal the river. Enter card: ")
                utils.add_to_list(tabled_cards, str_remaining, remaining_deck, max_size=5)
            pot, folded_players, player_max_earnings = self.post_flop_bet(dealer_idx, pot, folded_players, player_max_earnings, tabled_cards)
            say(f"pot is now {pot}")
            if sum(folded_players) >= len(self.players)-1:
                say("all players have folded. distributing wealth")
            self.distribute_wealth(pot, folded_players, player_max_earnings, tabled_cards)
            dealer_idx = self.check_lost_players(dealer_idx)%len(self.players)
            




        pass

    def __computer_game(self, verbose):
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
    t = table(player_constructors=[random.constructor, random.constructor, random.constructor, random.constructor],player_names=["1", "2", "3", "4"],starting_money=10)
    for p in t.players:
        print(p.get_name(),":",type(p))
    t.play_game()