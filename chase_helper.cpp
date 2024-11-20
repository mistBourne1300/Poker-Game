#include <iostream>
#include <string>
#include <sstream>
#include <cmath>

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

int main(const int argc, const char* argv[]){
    int* card;
    string strCard;
    int buckets[10] = {0,0,0,0,0,0,0,0,0,0};
    int currHand[7][2] = {{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0}};

    for(int i = 1; i < argc; i++){
        strCard = argv[i];
        card = card_to_tuple(strCard);
        currHand[i-1][0] = card[0];
        currHand[i-1][1] = card[1];
    }
    cout << hand_to_string(argc-1,currHand) << endl;
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
        ss << ", " << RANKS[hand[i][0]] << SUITS[hand[i][1]];
    }
    ss << "]";
    return ss.str();
}

