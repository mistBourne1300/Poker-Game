#include <iostream>
#include <string>
#include <sstream>
#include <bits/stdc++.h>

using namespace std;

int* card_to_tuple(string strCard);
string hand_to_string(int hand[7][2]);
void combination(int (&buckets)[10], int hand_size, int curr_hand[7][2]);
void combination_rec(int (&buckets)[10], int hand_size, int curr_hand[7][2]);
void best_hand(int (&buckets)[10], int hand[7][2]);
int* straight(int hand_size, int hand[]);

int main(const int argc, const char* argv[]) {
    int handSize = argc;
    int* card;
    string strCard;
    int buckets[10];
    int curr_hand[7][2] = {{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0}};
    for (int i = 1; i < argc; i++) {
        strCard = argv[i];
        card = card_to_tuple(strCard);
        curr_hand[i - 1][0] = card[0];
        curr_hand[i - 1][1] = card[1];
    }
    combination(buckets, argc - 1, curr_hand);

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
    ss << "[(" << hand[0][0] << "," << hand[0][1] << ")";
    for (int i = 1; i < 7; i++) {
        ss << ", (" << hand[i][0] << "," << hand[i][1] << ")";
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
        best_hand(buckets,curr_hand);
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
        best_hand(buckets,curr_hand);
    }
}

void best_hand(int (&buckets)[10], const int hand[7][2]) {
    // check for a flush
    int suits[4] = {0,0,0,0}; // tally of how many of each suit there are
    for (int i = 0; i < 7; i++) { suits[hand[i][1]]++; } // count each suit
    int num_suited = 0; // number of cards in the suit with the most cards in it
    for (int i = 0; i < 4; i++) { if (num_suited < suits[i]) num_suited = suits[i]; }

    if (num_suited > 4) {
        // find which suit has the flush
        int flush_suit = 0;
        for (int i = 1; i < 4; i++) { if (suits[i] > suits[flush_suit]) flush_suit = i; }
        // extract the ranks of the cards in the flush suit
        int cards_in_suit[num_suited];
        int j = 0;
        for (int i = 0; i < 7; i++) { if (hand[i][1] == flush_suit) { cards_in_suit[j] = hand[i][0]; j++; } }
        sort(hand, hand + num_suited, greater<int>());

    }
    else {

    }
    cout << hand_to_string(hand) << endl;
}

int* straight(const int hand_size, const int hand[]) {
    static int straight[5] = {0,0,0,0,0};
    int j;
    for (int i = 0; i < hand_size - 4; i++) {
        straight[0] = hand[i];
        for (j = 0; j < 5; j++) {
            if (hand[i + j + 1] != hand[i + j] - 1) { break; }
            straight[j + 1] = hand[i + j + 1];
        }
        if (j > 4) { break; }
        for (int k = 0; k < 5; k++) { straight[k] = 0; }
    }
    return straight;
}