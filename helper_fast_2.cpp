#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <cmath>
#include "Cards.h"
// #include <bits/locale_conv.h>

using namespace std;

// Tweakable Constants
const int PERCENT_DECIMALS = 5;

void generate_combinations(const int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude);
void generate_combinations_rec(const int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude);

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

void generate_combinations(const int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude) {
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

void generate_combinations_rec(const int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude) {
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

