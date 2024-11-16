#include <iostream>
#include <string>
#include <sstream>
#include <bits/stdc++.h>

using namespace std;

const string RANKS[15] = {"0", "0", "2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"};
const string SUITS[4] = {"s", "h", "c", "d" };
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

int* card_to_tuple(string strCard);
string hand_to_string(const int hand[7][2]);
void combination(int (&buckets)[10], int hand_size, int curr_hand[7][2]);
void combination_rec(int (&buckets)[10], int hand_size, int curr_hand[7][2]);
void find_best_hand(int (&buckets)[10], const int hand[7][2]);
int* find_straight(int hand_size, const int hand[]);

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
    combination(buckets, argc - 1, curr_hand);
    for (int i = 0; i < 10; i++) { cout << buckets[i] << " "; }
    cout << endl;

    return 0;
}

int* card_to_tuple(string strCard) {
    static int intCard[2];
    switch (strCard[strCard.size()-1]) {
        case 's':
            intCard[1] = 0;
            break;
        case 'h':
            intCard[1] = 1;
            break;
        case 'c':
            intCard[1] = 2;
            break;
        case'd':
            intCard[1] = 3;
            break;
        default:
            break;
    }
    strCard.pop_back();
    if (strCard == "j") { intCard[0] = 11; }
    else if (strCard == "q") { intCard[0] = 12; }
    else if (strCard == "k") { intCard[0] = 13; }
    else if (strCard == "a") { intCard[0] = 14; }
    else { intCard[0] = stoi(strCard); }
    return intCard;
}

string hand_to_string(const int hand[7][2]) {
    stringstream ss;
    ss << "[" << RANKS[hand[0][0]] << SUITS[hand[0][1]];
    for (int i = 1; i < 7; i++) {
        ss << "] [" << RANKS[hand[i][0]] << SUITS[hand[i][1]];
    }
    ss << "]";
    return ss.str();
}

void combination(int (&buckets)[10], const int hand_size, int curr_hand[7][2]) {
    if (hand_size < 7) {
        bool should_pass;
        for (int i = 0; i < 4; i++) {
            for (int j = 2; j < 15; j++) {
                should_pass = false;
                for (int k = 0; k < 7; k++) { if (curr_hand[k][0] == j && curr_hand[k][1] == i) { should_pass = true; break; } }
                if (should_pass){ continue; }

                curr_hand[hand_size][0] = j; curr_hand[hand_size][1] = i;
                combination_rec(buckets, hand_size + 1, curr_hand);
            }
        }
    }
    else {
        find_best_hand(buckets, curr_hand);
    }
}

void combination_rec(int (&buckets)[10], const int hand_size, int curr_hand[7][2]) {
    if (hand_size < 7) {
        bool should_pass;
        bool is_first_iter = true;
        for (int i = 0; i < 4; i++) {
            if (is_first_iter) { i = curr_hand[hand_size-1][1]; }
            for (int j = 2; j < 15; j++) {
                if (is_first_iter) { j = curr_hand[hand_size-1][0]; is_first_iter = false; }
                should_pass = false;
                for (int k = 0; k < 7; k++) { if (curr_hand[k][0] == j && curr_hand[k][1] == i) { should_pass = true; break; } }
                if (should_pass){ continue; }

                curr_hand[hand_size][0] = j; curr_hand[hand_size][1] = i;
                combination_rec(buckets, hand_size + 1, curr_hand);
            }
        }
    }
    else {
        find_best_hand(buckets, curr_hand);
    }
}

void find_best_hand(int (&buckets)[10], const int hand[7][2]) {
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
        int cards_in_suit[num_suited];
        { int j = 0; for (int i = 0; i < 7; i++) { if (hand[i][1] == flush_suit) { cards_in_suit[j] = hand[i][0]; j++; } } }
        sort(cards_in_suit, cards_in_suit + num_suited, greater<>());
        // check if there is a straight
        const int* straight = find_straight(num_suited, cards_in_suit);
        // process the data from straight
        if (straight[0] == 0) { buckets[FLUSH]++; return; }
        if (straight[0] == 14) { buckets[ROYAL_FLUSH]++; return; }
        buckets[STRAIGHT_FLUSH]++; return;
    }
    else {

    }
}

int* find_straight(const int hand_size, const int hand[]) {
    static int straight[5] = {0,0,0,0,0};
    int j;
    for (int i = 0; i < hand_size - 4; i++) {
        straight[0] = hand[i];
        for (j = 0; j < 5; j++) {
            if (hand[i + j + 1] != hand[i + j] - 1) { break; }
            straight[j + 1] = hand[i + j + 1];
        }
        if (j > 3) { break; } // if the above code finds a whole straight, don't reset straight and exit the loop
        for (int k = 0; k < 5; k++) { straight[k] = 0; }
    }
    return straight;
}
