#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <execution>
#include <algorithm>
#include <cmath>
#include <thread>
#include <omp.h>
#include <iomanip>

#include "Cards.h"
// #include <bits/locale_conv.h>

using namespace std;

// Quality of life constants
const string HANDS[10] = {"High Card", "Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"};

// Tweakable Constants
constexpr int PERCENT_DECIMALS = 5;

void generate_combinations(int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude);
void generate_combinations_rec(int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> const &options, int curr_index);
Hand find_best_hand(vector<Card> hand);
vector<Card> find_straight(vector<Card> hand);
void kind_sort(vector<Card> &hand);

int main(const int argc, const char* argv[]) {
  int buckets[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  int winTally[2] = {0,0};
  vector<Card> cardsInPlay;
  const int num_players = stoi(argv[1]);
  for (int i = 2; i < argc; i++) { cardsInPlay.push_back(Card(argv[i])); }
  vector<vector<Card>> combinations;
  cout << "Generating all possible hands..." << endl;
	generate_combinations(7, combinations, cardsInPlay,  {});
  const int NUM_COMBOS = combinations.size();
  static int curr_iter = 0;
  static float benchmark = 0;
  #pragma omp parallel
  {
    if (omp_get_thread_num() == 0) cout << "Calculating win probabilities using " << omp_get_num_threads() << " threads..." << endl;
    #pragma omp for
    for (auto combo : combinations) {
  	    vector<Card> table;
  	    for (int i = 2; i < 7; ++i) { table.push_back(combo.at(i)); }
  	    vector<Card> myHand;
  	    for (int i = 0; i < 2; ++i) { myHand.push_back(combo.at(i)); }
  	    vector<Card> myCards;
  	    for (int i = 0; i < 7; ++i) { myCards.push_back(combo.at(i)); }
  	    Hand myBestHand = find_best_hand(myCards);
          buckets[myBestHand.getType() - 1]++;

  	    // Do opponent calculations
  	    int num_players_temp = min(num_players, 2); // temporarily cap number of opponents to 1 until I get that case working
  	    for (int playerNum = 1; playerNum < num_players_temp; ++playerNum) {
  	        vector<vector<Card>> oppCombos;
  	        generate_combinations(7, oppCombos, table, myHand);
  	        for (vector<Card> oppCombo : oppCombos) {
  	            Hand oppBestHand = find_best_hand(oppCombo);
  	            if (oppBestHand < myBestHand) { ++winTally[0]; }
  	            ++winTally[1];
  	        }
  	    }
        #pragma omp critical
        {
          // cout << benchmark << "% complete\r";
          if ((++curr_iter * 1000)/NUM_COMBOS/10.0 >= benchmark) {
            cout << flush << setprecision(1) << fixed << benchmark << "% complete\r";
            benchmark += .1;
          }
        }
      } // for loop
    } // parallel block
    // for (int i = 0; i < 10; i++) { cout << buckets[i] << " "; } // uncomment to see exact bucket values
    cout << "------------          " << endl;
    int total_hands = 0;
    for (int i = 0; i < 10; i++) { total_hands += buckets[i]; }
    for (int i = 9; i > -1; i--) {
        cout << HANDS[i] << ":";
        for (int j = HANDS[i].length(); j < 16; j++) { cout << " "; } // align percentages. 16 comes from the fact that "Three of a Kind" has 15 characters
        cout << trunc(buckets[i] * pow(10, PERCENT_DECIMALS + 2)/total_hands)/pow(10, PERCENT_DECIMALS) << "%" << endl;
    }
    if (winTally[1] > 0) {
        cout << "------------" << endl;
        cout << "Win chance:      " << trunc(winTally[0] * pow(10, PERCENT_DECIMALS + 2)/winTally[1])/pow(10, PERCENT_DECIMALS) << "%" << endl;
    }
    return 0;
}

void generate_combinations(int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> cards_to_exclude) {
    if (curr_hand.size() < hand_size) {
        vector<Card> options;
        Card tempCard;
        bool shouldAdd;
        for (Suit suit = DIAMONDS; suit < SUIT_COUNT; ++suit) {
            for (Rank rank = TWO; rank < RANK_COUNT; ++rank) {
                shouldAdd = true;
                tempCard = Card(rank, suit);
                for (Card card : curr_hand)        { if (tempCard == card) { shouldAdd = false; break; } }
                for (Card card : cards_to_exclude) { if (tempCard == card) { shouldAdd = false; break; } }
                if (shouldAdd) { options.push_back(tempCard); }
            }
        }
        vector<int> indices;
        for (int i = 0; i < options.size(); ++i) { indices.push_back(i); }
        for_each(execution::par, indices.begin(), indices.end(), [&options, &curr_hand, hand_size, &combinations](int i) {
            curr_hand.push_back(options.at(i));
            generate_combinations_rec(hand_size, combinations, curr_hand, options, i);
            curr_hand.pop_back();
        });
    }
    else {
    	combinations.push_back(curr_hand);
    }

}

void generate_combinations_rec(int hand_size, vector<vector<Card>> &combinations, vector<Card> curr_hand, vector<Card> const &options, int curr_index) {
    if (curr_hand.size() < hand_size) {
        for (int i = curr_index + 1; i < options.size(); ++i) {
            curr_hand.push_back(options.at(i));
            generate_combinations_rec(hand_size, combinations, curr_hand, options, i);
            curr_hand.pop_back();
        }
    }
    else {
        combinations.push_back(curr_hand);
    }
}

Hand find_best_hand(vector<Card> hand) {
    if (hand.size() != 7) {throw "Best hand is only defined for 7 card hands";}
    // check for a flush
    int suits[5] = {0,0,0,0,0}; // tally of how many of each suit there are. 0th entry counts NULL_SUIT
    for (Card card : hand) { suits[card.getSuit()]++; } // count each suit
    int num_suited = 0; // number of cards in the suit with the most cards in it
    for (int i = 0; i < 5; i++) { if (num_suited < suits[i]) { num_suited = suits[i]; } }

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
        // check if there is a straight
        sort(cards_in_suit.begin(), cards_in_suit.end(), [](const Card &a, const Card &b) { return a > b; }); // FLUSH does need this sorted regardless of straight
        vector<Card> straight = find_straight(cards_in_suit);
        // process the data from straight
        switch (straight.at(0).getRank()) {
            case NULL_RANK:
                return {FLUSH, {cards_in_suit.begin(), cards_in_suit.begin() + 5}};
            case ACE:
                return {ROYAL_FLUSH, straight};
            default:
                return {STRAIGHT_FLUSH, straight};
        }
    }
    else {
        vector<Card> sorted_hand = hand;
        kind_sort(sorted_hand);

        // Four of a Kind
        if (sorted_hand.at(0).getRank() == sorted_hand.at(3).getRank()) {
            vector<Card> best_hand(sorted_hand.begin(), sorted_hand.begin() + 4);
            best_hand.push_back(max(sorted_hand.at(4), sorted_hand.at(6))); // It's possible that the two cards after the four of a kind are a pair of lower rank than the highest rank remaining
            return {FOUR_OF_A_KIND, best_hand};
        }

        // Full House
        if (sorted_hand.at(0).getRank() == sorted_hand.at(2).getRank() && sorted_hand.at(3).getRank() == sorted_hand.at(4).getRank()) { return {FULL_HOUSE, {sorted_hand.begin(), sorted_hand.begin() + 5}}; }

        // Straight
        sort(hand.begin(), hand.end(), [](const Card &a, const Card &b) { return a > b; });
        vector<Card> straight = find_straight(hand);
        if (straight.at(0).getRank() != 0) { return {STRAIGHT, straight}; }

        // Three of a Kind
        if (sorted_hand.at(0).getRank() == sorted_hand.at(2).getRank()) { return {THREE_OF_A_KIND, {sorted_hand.begin(), sorted_hand.begin() + 5}}; }

        // Two Pair
        if (sorted_hand.at(2).getRank() == sorted_hand.at(3).getRank()) {
            vector<Card> best_hand(sorted_hand.begin(), sorted_hand.begin() + 4);
            best_hand.push_back(max(sorted_hand.at(4), sorted_hand.at(6))); // It's possible that the two cards after the two pair are a pair of lower rank than the highest rank remaining
            return {TWO_PAIR, best_hand};
        }

        // Pair
        if (sorted_hand.at(0).getRank() == sorted_hand.at(1).getRank()) { return {PAIR, {sorted_hand.begin(), sorted_hand.begin() + 5}}; }

        // High Card
        return {HIGH_CARD, {sorted_hand.begin(), sorted_hand.begin() + 5}};
    }
}

vector<Card> find_straight(vector<Card> hand) {
    // hand should be sorted before being passed to streamline this process
    // sort(hand.begin(), hand.end(), [](const Card &a, const Card &b) { return a > b; });
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
    return {Card()};
}

void kind_sort(vector<Card> &hand) {
    int counts[15] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    for (Card card : hand) { counts[card.getRank()]++; }
    int num_ranks = 0;
    int num_sorted = 0;
    for (int i = 2; i < 15; i++) { num_ranks += (counts[i] != 0); }
    for (int j = 0; j < num_ranks; j++) {
        Rank max_rank = ACE;
        for (int i = 13; i > 1; i--) { if (counts[i] > counts[max_rank]) { max_rank = static_cast<Rank>(i); } } // find most common card. A tie goes to the higher value
        for (Card &card1 : hand) {
            for (Card &card2 : hand) {
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
