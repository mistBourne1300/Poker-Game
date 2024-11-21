#include <iostream>
#include <string>
#include <sstream>
#include <cmath>
// #include <bits/locale_conv.h>

using namespace std;

// Conversion Constants, DO NOT EDIT
const string RANKS[15] = {"0", "0", "2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"};
const string SUITS[4] = {"d", "c", "h", "s" };
const string HANDS[10] = {"High Card", "Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"};
const int ROYAL_FLUSH = 9;
const int STRAIGHT_FLUSH = 8;
const int FOUR_OF_A_KIND = 7;
const int FULL_HOUSE = 6;
const int FLUSH = 5;
const int STRAIGHT = 4;
const int THREE_OF_A_KIND = 3;
const int TWO_PAIR = 2;
const int PAIR = 1;
const int HIGH_CARD = 0;

// Tweakable Constants
const int PERCENT_DECIMALS = 5;

int* card_to_tuple(string strCard);
string hand_to_string(int hand_len, const int hand[][2]);
void combination(int (&buckets)[10], int hand_size, int curr_hand[7][2], int num_to_exclude, int cards_to_exclude[][2]);
void combination_rec(int (&buckets)[10], int hand_size, int curr_hand[7][2], int num_to_exclude, int cards_to_exclude[][2]);
void find_best_hand(int (&buckets)[10], int hand[7][2]);
void find_straight(int hand_size, const int hand[][2], int (&straight)[5][2]);
void sort_descending(int hand_size, int (&hand)[][2]);
void kind_sort(int hand_size, int (&hand)[][2]);

int main(const int argc, const char* argv[]) {
    int* card;
    string strCard;
    int buckets[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    int curr_hand[7][2] = {{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0}};

    for (int i = 1; i < argc; i++) {
        strCard = argv[i];
        card = card_to_tuple(strCard);
        curr_hand[i - 1][0] = card[0]; curr_hand[i - 1][1] = card[1];
    }
    int cardsToExclude[0][2] = {};
    combination(buckets, argc - 1, curr_hand, 0, cardsToExclude);
    for (int i = 0; i < 10; i++) { cout << buckets[i] << " "; }
    cout << endl;
    int total_hands = 0;
    for (int i = 0; i < 10; i++) { total_hands += buckets[i]; }
    for (int i = 9; i > -1; i--) {
        cout << HANDS[i] << ":";
        for (int j = HANDS[i].length(); j < 16; j++) { cout << " "; } // align percentages. 16 comes from the fact that "Three of a Kind" has 15 characters
        cout << trunc(buckets[i] * pow(10, PERCENT_DECIMALS + 2)/total_hands)/pow(10, PERCENT_DECIMALS) << "%" << endl;
    }

    return 0;
}

int* card_to_tuple(string strCard) {
    static int intCard[2];
    switch (strCard[strCard.size()-1]) {
        case 'd': intCard[1] = 0; break;
        case 'c': intCard[1] = 1; break;
        case 'h': intCard[1] = 2; break;
        case 's': intCard[1] = 3; break;
        default: break; // FIXME: add error handling
    }
    strCard.pop_back();
    if (strCard == "j") { intCard[0] = 11; }
    else if (strCard == "q") { intCard[0] = 12; }
    else if (strCard == "k") { intCard[0] = 13; }
    else if (strCard == "a") { intCard[0] = 14; }
    else if ( 1 < stoi(strCard) && stoi(strCard) < 11) { intCard[0] = stoi(strCard); }
    else {} // FIXME: add error handling
    return intCard;
}

string hand_to_string(const int hand_len, const int hand[][2]) {
    stringstream ss;
    ss << "[" << RANKS[hand[0][0]] << SUITS[hand[0][1]];
    for (int i = 1; i < hand_len; i++) {
        ss << "] [" << RANKS[hand[i][0]] << SUITS[hand[i][1]];
    }
    ss << "]";
    return ss.str();
}

void combination(int (&buckets)[10], const int hand_size, int curr_hand[7][2], int num_to_exclude, int cards_to_exclude[][2]) {
    if (hand_size < 7) {
        bool should_pass;
        for (int i = 0; i < 4; i++) {
            for (int j = 2; j < 15; j++) {
                should_pass = false;
                for (int k = 0; k < 7; k++) { if (curr_hand[k][0] == j && curr_hand[k][1] == i) { should_pass = true; break; } }
                for (int k = 0; k < num_to_exclude; k++) { if (cards_to_exclude[k][0] == j && cards_to_exclude[k][1] == i) { should_pass = true; break; } }
                if (should_pass){ continue; }

                curr_hand[hand_size][0] = j; curr_hand[hand_size][1] = i;
                combination_rec(buckets, hand_size + 1, curr_hand, num_to_exclude, cards_to_exclude);
            }
        }
    }
    else {
        find_best_hand(buckets, curr_hand);
    }
}

void combination_rec(int (&buckets)[10], const int hand_size, int curr_hand[7][2], int num_to_exclude, int cards_to_exclude[][2]) {
    if (hand_size < 7) {
        bool should_pass;
        bool is_first_iter = true;
        for (int i = 0; i < 4; i++) {
            if (is_first_iter) { i = curr_hand[hand_size-1][1]; }
            for (int j = 2; j < 15; j++) {
                if (is_first_iter) { j = curr_hand[hand_size-1][0]; is_first_iter = false; }
                should_pass = false;
                for (int k = 0; k < 7; k++) { if (curr_hand[k][0] == j && curr_hand[k][1] == i) { should_pass = true; break; } }
                for (int k = 0; k < num_to_exclude; k++) { if (cards_to_exclude[k][0] == j && cards_to_exclude[k][1] == i) { should_pass = true; break; } }
                if (should_pass){ continue; }

                curr_hand[hand_size][0] = j; curr_hand[hand_size][1] = i;
                combination_rec(buckets, hand_size + 1, curr_hand, num_to_exclude, cards_to_exclude);
            }
        }
    }
    else {
        find_best_hand(buckets, curr_hand);
    }
}

void find_best_hand(int (&buckets)[10], int hand[7][2]) {
    int best_hand[6][2];
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

void find_straight(const int hand_size, const int hand[][2], int (&straight)[5][2]) {
    int out_i;
    for (int i = 0; i < hand_size - 4; i++) {
        straight[0][0] = hand[i][0]; straight[0][1] = hand[i][1];
        out_i = 1;
        for (int j = 1; j < hand_size; j++) {
            if (hand[j][0] < straight[out_i - 1][0] - 1) { break; }
            if (hand[j][0] == straight[out_i - 1][0] - 1) {
                straight[out_i][0] = hand[j][0]; straight[out_i][1] = hand[j][1];
                out_i++;
            }
        }
        if (out_i > 4) { return; } // if the above code finds a whole straight, be done
        for (int k = 0; k < 5; k++) { straight[k][0] = 0; straight[k][1] = 0; }
    }
}

void sort_descending(int hand_size, int (&hand)[][2]) {
    // I know it's not an efficient algorithm, I just needed it to work
    int card[2] = {0, 0};
    for (int i = 0; i < hand_size; i++) {
        for (int j = i + 1; j < hand_size; j++) {
            if (hand[i][0] < hand[j][0] || (hand[i][0] == hand[j][0] && hand[i][1] < hand[j][1])) {
                card[0] = hand[i][0]; card[1] = hand[i][1];
                hand[i][0] = hand[j][0]; hand[i][1] = hand[j][1];
                hand[j][0] = card[0]; hand[j][1] = card[1];
            }
        }
    }
}

void kind_sort(int hand_size, int (&hand)[][2]) {
    int counts[15] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    for (int i = 0; i < hand_size; i++) { counts[hand[i][0]]++; }
    int num_ranks = 0;
    int num_sorted = 0;
    int card[2] = {0,0};
    for (int i = 2; i < 15; i++) { num_ranks += (counts[i] != 0); }
    for (int j = 0; j < num_ranks; j++) {
        int max_rank = 14;
        for (int i = 13; i > 1; i--) { if (counts[i] > counts[max_rank]) { max_rank = i; } } // find most common card. A tie goes to the higher value
        for (int i = num_sorted; i < hand_size; i++) {
            for (int k = i + 1; k < hand_size; k++) {
                if ((hand[i][0] != max_rank && hand[k][0] == max_rank) || (hand[i][0] == max_rank && hand[k][0] == max_rank && hand[i][1] < hand[k][1])) {
                    card[0] = hand[i][0]; card[1] = hand[i][1];
                    hand[i][0] = hand[k][0]; hand[i][1] = hand[k][1];
                    hand[k][0] = card[0]; hand[k][1] = card[1];
                }
            }
        }
        num_sorted += counts[max_rank];
        counts[max_rank] = 0;
    }
}
