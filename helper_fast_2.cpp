#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <execution>
#include <algorithm>
#include <cmath>
#include "Cards.h"
// #include <bits/locale_conv.h>

using namespace std;

// Tweakable Constants
constexpr int PERCENT_DECIMALS = 5;

void generate_combinations(int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude);
void generate_combinations_rec(int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude);
Hand find_best_hand(vector<Card> hand);
vector<Card> find_straight(vector<Card> hand);
void kind_sort(vector<Card> &hand);

int main(const int argc, const char* argv[]) {
    int buckets[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    vector<Card> hand;
    for (int i = 1; i < argc; i++) { hand.push_back(Card(argv[i])); }
    vector<vector<Card>> combinations;
	generate_combinations(7, combinations, hand, vector<Card> {});
	for_each(execution::par, combinations.begin(), combinations.end(), [](vector<Card> &hand) {
        Hand myBestHand = find_best_hand(hand);
	});
    return 0;
}

void generate_combinations(int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude) {
    if (curr_hand.size() < hand_size) {
    	Card card;
        bool should_pass;
        for (Suit suit = DIAMONDS; suit < SUIT_COUNT; suit++) {
            for (Rank rank = TWO; rank < RANK_COUNT; rank++) {
                should_pass = false;
                card = Card(rank, suit);
                for (int i = 0; i < curr_hand.size(); i++)        { if (card == curr_hand.at(i)) { should_pass = true; break; } }
                for (int i = 0; i < cards_to_exclude.size(); i++) { if (card == cards_to_exclude.at(i)) { should_pass = true; break; } }
                if (should_pass){ continue; }
                curr_hand.push_back(card);
                generate_combinations_rec(hand_size, combinations, curr_hand, cards_to_exclude);
                curr_hand.pop_back();
            }
        }
    }
    else {
    	combinations.push_back(curr_hand);
    }

}

void generate_combinations_rec(int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude) {
    if (curr_hand.size() < hand_size) {
      	Card card;
        bool should_pass;
        bool is_first_iter = true;
        for (Suit suit = DIAMONDS; suit < SPADES; suit++) {
            for (Rank rank = TWO; rank < ACE; rank++) {
                if (is_first_iter) {
                  suit = curr_hand.back().getSuit();
                  rank = curr_hand.back().getRank();
                  is_first_iter = false;
                }
                should_pass = false;
             	card = Card(rank, suit);
              	for (int i = 0; i < curr_hand.size(); i++)        { if (card == curr_hand.at(i)) { should_pass = true; break; } }
              	for (int i = 0; i < cards_to_exclude.size(); i++) { if (card == cards_to_exclude.at(i)) { should_pass = true; break; } }
              	if (should_pass){ continue; }
              	curr_hand.push_back(card);
              	generate_combinations_rec(hand_size, combinations, curr_hand, cards_to_exclude);
                curr_hand.pop_back();
            }
        }
    }
    else {
        combinations.push_back(curr_hand);
    }
}

Hand find_best_hand(vector<Card> hand) {
    // check for a flush
    int suits[5] = {0,0,0,0,0}; // tally of how many of each suit there are
    for (Card card : hand) { suits[card.getSuit()]++; } // count each suit
    int num_suited = 0; // number of cards in the suit with the most cards in it
    for (int i = 0; i < 4; i++) { if (num_suited < suits[i]) { num_suited = suits[i]; } }

    if (num_suited > 4) {
        // find which suit has the flush
        Suit flush_suit = NULL_SUIT;
        for (int i = 1; i < 5; i++) { if (suits[i] > suits[flush_suit]) flush_suit = static_cast<Suit>(i); }
        // extract the cards in the flush suit
        vector<Card> cards_in_suit;
        for (Card card : hand) {
            if (card.getSuit() == flush_suit) {
                cards_in_suit.push_back(card);
            }
        }
        sort(cards_in_suit.begin(), cards_in_suit.end(), [](const Card &a, const Card &b) { return a > b; });
        // check if there is a straight
        vector<Card> straight = find_straight(cards_in_suit);
        // process the data from straight
        switch (straight.at(0).getRank()) {
            case NULL_RANK:
                return {FLUSH, vector<Card>(cards_in_suit.begin(), cards_in_suit.begin() + 5)};
            case ACE:
                return {ROYAL_FLUSH, straight};
            default:
                return {STRAIGHT_FLUSH, straight};
        }
    }
    else {
        vector<Card> straight = find_straight(hand);
        vector<Card> sorted_hand = hand;
        kind_sort(sorted_hand);
        if (hand.at(0).getRank() == hand.at(3).getRank()) {
            Card high_card = hand.at(4);
            for (Card card : vector<Card> {hand.begin() + 4, hand.end()}) {
                if (card > high_card) {
                    high_card = card;
                }
            }
            sorted_hand.at(4) = high_card; // huge abuse of notation, but works since sorted_hand is a dummy copy
            return {FOUR_OF_A_KIND, vector<Card>(sorted_hand.begin(), sorted_hand.begin() + 5)};
        }
        else if (sorted_hand.at(0).getRank() == sorted_hand.at(2).getRank() && sorted_hand.at(3).getRank() == sorted_hand.at(4).getRank()) {
            return {FULL_HOUSE, vector<Card> };
        }
        else if (straight[0][0] != 0) {
            buckets[STRAIGHT]++;
            best_hand[0][0] = STRAIGHT;
            for (int i = 1; i < 6; i++) { best_hand[i][0] = straight[i - 1][0]; best_hand[i][1] = straight[i - 1][1]; }
        }
        else if (new_hand[0][0] == new_hand[2][0]) {
            buckets[THREE_OF_A_KIND]++;
            best_hand[0][0] = THREE_OF_A_KIND;
            for (int i = 1; i < 4; i++) { best_hand[i][0] = new_hand[i - 1][0]; new_hand[i][1] = new_hand[i - 1][1]; }
            int high_card = 4;
            int sec_card;
            for (int i = 5; i < 7; i++) { if (new_hand[i][0] > new_hand[high_card][0]) { high_card = i; } }
            if (high_card = 4) { sec_card = 5; } else { sec_card = 4; }
            for (int i = 5; i < 7; i++) { if (new_hand[i][0] > new_hand[sec_card][0] && i != high_card) { sec_card = i; } }
            best_hand[4][0] = new_hand[high_card][0]; best_hand[4][0] = new_hand[high_card][1];
            best_hand[5][0] = new_hand[sec_card][0]; best_hand[5][0] = new_hand[sec_card][1];
        }
        else if (new_hand [2][0] == new_hand[3][0]) {
            buckets[TWO_PAIR]++;
            best_hand[0][0] = TWO_PAIR;
            for (int i = 1; i < 5; i++) { best_hand[i][0] = new_hand[i - 1][0]; new_hand[i][1] = new_hand[i - 1][1]; }
            int high_card = 5;
            for (int i = 6; i < 7; i++) { if (new_hand[i][0] > new_hand[high_card][0]) { high_card = i; } }
            best_hand[5][0] = new_hand[high_card][0]; best_hand[5][0] = new_hand[high_card][1];
        }
        else if (new_hand[0][0] == new_hand[1][0]) {
            buckets[PAIR]++;
            best_hand[0][0] = PAIR;
            for (int i = 1; i < 3; i++) { best_hand[i][0] = new_hand[i - 1][0]; new_hand[i][1] = new_hand[i - 1][1]; }
            int high_card = 3;
            int sec_card;
            int trd_card;
            for (int i = 4; i < 7; i++) { if (new_hand[i][0] > new_hand[high_card][0]) { high_card = i; } }
            if (high_card == 3) { sec_card = 4; } else { sec_card = 3; }
            for (int i = 3; i < 7; i++) { if (new_hand[i][0] > new_hand[sec_card][0] && i != high_card) { sec_card = i; } }
            if (high_card > 3 && sec_card > 3) { trd_card = 4; }
            else if (high_card < 6 && sec_card < 6) { trd_card = 3; }
            else { trd_card = 4;}
            for (int i = 3; i < 7; i++) { if (new_hand[i][0] > new_hand[trd_card][0] && i != high_card && i != sec_card) { trd_card = i; } }
            best_hand[3][0] = new_hand[high_card][0]; best_hand[3][0] = new_hand[high_card][1];
            best_hand[4][0] = new_hand[sec_card][0]; best_hand[4][0] = new_hand[sec_card][1];
            best_hand[5][0] = new_hand[trd_card][0]; best_hand[5][0] = new_hand[trd_card][1];
        }
        else {
            buckets[HIGH_CARD]++;
            best_hand[0][0] = HIGH_CARD;
            sort_descending(7, new_hand);
            for (int i = 0; i < 5; i++) { best_hand[i + 1][0] = new_hand[i][0]; best_hand[i + 1][1] = new_hand[i][1]; }
        }
    }
    // Calculate win percentages against opponents
    int opp_buckets[10] = {0,0,0,0,0,0,0,0,0,0};
    int opp_hand[7][2] = {{0,0},{0,0},{0,0},{0,0},{0,0},{0,0}};
    for (int i = 0; i < 5; i++) { opp_hand[i][0] = hand[i + 2][0]; opp_hand[i][1] = hand[i + 2][1]; }
    int my_hand[2][2] = {{hand[0][0],hand[0][1]},{hand[1][0],hand[1][1]}};
    // combination(opp_buckets,7,opp_hand,2,my_hand);
    int num_win_cases = 0;
    int num_cases = 0;
}

vector<Card> find_straight(vector<Card> hand) {
    sort(hand.begin(), hand.end(), [](const Card &a, const Card &b) { return a > b; });
    vector<Card> straight;
    for (int i = 0; i < hand.size() - 4; i++) {
        straight.push_back(hand.at(i));
        for (int j = 1; j < 5; j++) {
            if (hand.at(j).getRank() < straight.back().getRank() - 1) { break; }
            if (hand.at(j).getRank() == straight.back().getRank() - 1) {
                straight.push_back(hand.at(i + j));
            }
        }
        if (straight.size() == 5) { return straight; } // if the above code finds a whole straight, be done
        straight.clear();
    }
    return vector<Card> {Card()};
}

void kind_sort(vector<Card> &hand) {
    int counts[15] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    for (Card card : hand) { counts[card.getRank()]++; }
    int num_ranks = 0;
    int num_sorted = 0;
    Card card;
    for (int i = 2; i < 15; i++) { num_ranks += (counts[i] != 0); }
    for (int j = 0; j < num_ranks; j++) {
        Rank max_rank = ACE;
        for (int i = 13; i > 1; i--) { if (counts[i] > counts[max_rank]) { max_rank = static_cast<Rank>(i); } } // find most common card. A tie goes to the higher value
        for (Card card1 : hand) {
            for (Card card2 : hand) {
                if ((card1.getRank() != max_rank && card2.getRank() == max_rank)
                    || (card1.getRank() == max_rank && card2.getRank() == max_rank && card1.getSuit() < card2.getSuit())) {
                    swap(card1, card2);
                }
            }
        }
        num_sorted += counts[max_rank];
        counts[max_rank] = 0;
    }
}