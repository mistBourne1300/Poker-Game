#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <cmath>
#include "Cards.h"
// #include <bits/locale_conv.h>

using namespace std;

// Tweakable Constants
constexpr int PERCENT_DECIMALS = 5;

void generate_combinations(int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude);
void generate_combinations_rec(int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude);
void find_best_hand(vector<Card> hand);

int main(const int argc, const char* argv[]) {
    int buckets[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    vector<Card> hand;
    for (int i = 1; i < argc; i++) { hand.push_back(Card(argv[i])); }
    vector<vector<Card>> combinations;
	generate_combinations(7, combinations, hand, vector<Card> {});
	for (vector<vector<Card>>::iterator hand_ptr = combinations.begin(); hand_ptr != combinations.end(); hand_ptr++) {
    	for (vector<Card>::iterator card_ptr = hand_ptr->begin(); card_ptr != hand_ptr->end(); card_ptr++) {
        	cout << card_ptr->toString() << " ";
        }
	    cout << endl;
	}
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

void find_best_hand(vector<Card> hand) {
    // check for a flush
    int suits[4] = {0,0,0,0}; // tally of how many of each suit there are
    for (int i = 0; i < 7; i++) { suits[hand[i][1]]++; } // count each suit
    int num_suited = 0; // number of cards in the suit with the most cards in it
    for (int i = 0; i < 4; i++) { if (num_suited < suits[i]) { num_suited = suits[i]; } }

    if (num_suited > 4) {
        // find which suit has the flush
        int flush_suit = 0;
        for (int i = 1; i < 4; i++) { if (suits[i] > suits[flush_suit]) flush_suit = i; }
        // extract the ranks of the cards in the flush suit
        int cards_in_suit[num_suited][2];
        int out_i = 0;
        for (int i = 0; i < 7; i++) {
            if (hand[i][1] == flush_suit) {
                cards_in_suit[out_i][0] = hand[i][0];
                cards_in_suit[out_i][1] = hand[i][1];
                out_i++;
            }
        }
        sort_descending(num_suited, cards_in_suit);
        // check if there is a straight
        int straight[5][2] = {{0,0},{0,0},{0,0},{0,0},{0,0}};
        find_straight(num_suited, cards_in_suit, straight);
        // process the data from straight
        if (straight[0][0] == 0) {
            buckets[FLUSH]++;
            best_hand[0][0] = FLUSH;
            for (int i = 1; i < 6; i++) { best_hand[i][0] = cards_in_suit[i - 1][0]; best_hand[i][1] = cards_in_suit[i - 1][1]; }
        }
        else if (straight[0][0] == 14) {
            buckets[ROYAL_FLUSH]++;
            best_hand[0][0] = ROYAL_FLUSH;
            for (int i = 1; i < 6; i++) { best_hand[i][0] = straight[i - 1][0]; best_hand[i][1] = straight[i - 1][1]; }
        }
        else {
            buckets[STRAIGHT_FLUSH]++;
            best_hand[0][0] = STRAIGHT_FLUSH;
            for (int i = 1; i < 6; i++) { best_hand[i][0] = straight[i - 1][0]; best_hand[i][1] = straight[i - 1][1]; }
        }
    }
    else {
        int new_hand[7][2];
        for (int i = 0; i < 7; i++) { new_hand[i][0] = hand[i][0]; new_hand[i][1] = hand[i][1]; }
        kind_sort(7, new_hand); // I don't know why this wouldn't just accept hand, so I made new_hand and it just worked
        int straight[5][2] = {{0,0},{0,0},{0,0},{0,0},{0,0}};
        find_straight(7, new_hand, straight);
        if (new_hand[0][0] == new_hand[3][0]) {
            buckets[FOUR_OF_A_KIND]++;
            best_hand[0][0] = FOUR_OF_A_KIND;
            for (int i = 1; i < 5; i++) { best_hand[i][0] = new_hand[i - 1][0]; best_hand[i][1] = new_hand[i - 1][1]; }
            int high_card = 4;
            for (int i = 5; i < 7; i++) { if (new_hand[i][0] > new_hand[high_card][0]) { high_card = i; } }
            best_hand[5][0] = new_hand[high_card][0]; best_hand[5][1] = new_hand[high_card][1];
        }
        else if (new_hand[0][0] == new_hand[2][0] && new_hand[3][0] == new_hand[4][0]) {
            buckets[FULL_HOUSE]++;
            best_hand[0][0] = FULL_HOUSE;
            for (int i = 1; i < 6; i++) { best_hand[i][0] = new_hand[i - 1][0]; best_hand[i][1] = new_hand[i - 1][1]; }
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