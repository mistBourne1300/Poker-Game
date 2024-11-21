#include <iostream>
#include <string>
#include <sstream>
#include <stdlib.h>
#include <cmath>
#include "cards.h"

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

Card strToCard(string strCard);
string handToString(int handLen, Card hand[]);
bool checkInHand(int handLen, const Card hand[], Card card);
bool addToHand(int handLen, Card hand[]);
void displayProbs(int handLen, Card hand[]);
void calcBuckets(int handLen, Card hand[7], int (&buckets)[10]);
void calcBestHand(Card hand[7], int (&results)[6]);
int containsStraight(const int (&rcount)[15]);
void highestKinds(int rcount[15], int (&countVals)[5][2]);
void nlargest(int arrSize, int vals[], int num, int maxima[]);



int main(const int argc, const char* argv[]){
    Card card;
    string strCard;
    Card currHand[7];


    for (int i = 1; i < argc; i++){
        strCard = argv[i];
        card = strToCard(strCard);
        currHand[i-1] = card;
    }
    int numInHand = argc-1;

    system("clear");
    while (numInHand < 2 ) {
        cout << "Your hand: " << handToString(numInHand,currHand) << endl;
        while (!addToHand(numInHand,currHand)) {}
        system("clear");
        numInHand++;
    }


    while (numInHand < 7) {
        system("clear");
        cout << "Your hand: " << handToString(numInHand,currHand) << endl;
        cout << "calculating combos" << endl;
        displayProbs(numInHand, currHand);
        while (!addToHand(numInHand,currHand)) {}
        numInHand++;
    }

    system("clear");
    cout << "Your hand: " << handToString(numInHand,currHand) << endl;
    int result[6] = {0};
    calcBestHand(currHand,result);
    cout << "best " << result[0] << endl;
}

Card strToCard(string strCard) {
    Rank r;
    Suit s;
    switch (strCard[strCard.size()-1]) {
        case 'd': s = DIAMONDS; break;
        case 'c': s = CLUBS; break;
        case 'h': s = HEARTS; break;
        case 's': s = SPADES; break;
        default:
            stringstream ss;
            ss << strCard << " is an invalid card name";
            throw std::invalid_argument(ss.str());
            break;
    }
    strCard.pop_back();
    if (strCard == "j") { r = JACK; }
    else if (strCard == "q") { r = QUEEN; }
    else if (strCard == "k") { r = KING; }
    else if (strCard == "a") { r = ACE; }
    else if ( 1 < stoi(strCard) && stoi(strCard) < 11) { r = static_cast<Rank>(stoi(strCard)); }
    else {
        stringstream ss;
        ss << strCard << " is an invalid card name";
        throw std::invalid_argument(ss.str());
    }
    Card newcard(r,s);
    return newcard;
}

string handToString(int handLen, Card hand[]) {
    stringstream ss;
    if (handLen > 0){
        ss << "[" << hand[0].toString();
    } else {
        ss << "[";
    }
    
    for (int i = 1; i < handLen; i++) {
        ss << ", " << hand[i].toString();
    }
    ss << "]";
    ss << " (" << handLen << " cards)";
    return ss.str();
}

bool checkInHand(int handLen, const Card hand[], Card card) {
    for (int i = 0; i < handLen; i++) {
        if (card == hand[i]) {
            return true;
        }
    }
    return false;
}

bool addToHand(int handLen, Card hand[]) {
    string strCard;
    Card card;
    cout << "enter card: ";
    cin >> strCard;
    cout << endl;
    try{
        card = strToCard(strCard);
        if (checkInHand(handLen, hand, card)) {
            cout << strCard << " already in hand. Try again." << endl;
            return false;
        }
        hand[handLen] = card;
        return true;
    } catch (std::invalid_argument except) {
        cout << strCard << " is not a valid card." << endl;
    }
    return false;
}

void displayProbs(int handLen, Card hand[]) {
    cout << "with " << handLen << " cards, you havs a 0% chance of winning" << endl;
    int buckets [10] = {0};
    Card workingHand[7];
    for(int i = 0; i < handLen; i++) {
        workingHand[i] = hand[i];
    }
    calcBuckets(handLen, workingHand, buckets);
    int bucketSum = 0;
    for (int i = 0; i < 10; i++) {
        cout << buckets[i] << " ";
        bucketSum += buckets[i];
    }
    cout << endl;
    double probs[10];
    for (int i = 0; i < 10; i++){
        probs[i] = (double)buckets[i]/(double)bucketSum;
    }
    cout << "Royal Flush: " << probs[9] << endl;
    cout << "Straight Flush: " << probs[8] << endl;
    cout << "Four Kind: " << probs[7] << endl;
    cout << "Full House: " << probs[6] << endl;
    cout << "Flush: " << probs[5] << endl;
    cout << "Straight: " << probs[4] << endl;
    cout << "Three Kind: " << probs[3] << endl;
    cout << "Two Pair: " << probs[2] << endl;
    cout << "Pair: " << probs[1] << endl;
    cout << "High Card: " << probs[0] << endl;
}

void calcBuckets(int handLen, Card hand[7], int (&buckets)[10]) {
    if (handLen == 7) {
        int result[6] = {0};
        calcBestHand(hand, result);
        buckets[result[0]] += 1;
        return;
    } else {
        Card newhand[7];
        for (int i = 0; i < handLen; i++) {
            newhand[i] = hand[i];
        }
        for (int r = 2; r < 15; r++) {// loop through the ranks
            Card newcard;
            for (int s = 0; s < 4; s++) {// loop through the suits
                newcard = Card(r,s);
                if (checkInHand(handLen, hand, newcard)) {
                    continue;
                } else {
                    newhand[handLen] = newcard;
                    calcBuckets(handLen+1, newhand, buckets);
                }
            }
        }
    }
}

void calcBestHand(Card hand[7], int (&results)[6]) {
    int scount[4] = {0};
    int rcount[15] = {0};
    for (int i = 0; i < 7; i++) {
        scount[hand[i].getSuit()]++;
    }
    bool flush = false;
    int idx = 0;
    for (int i = 0; i < 4; i++) {
        if (scount[i] > 4) {
            flush = true;
            idx = i;
            break;
        }
    }
    if (flush) {
        for (int i = 0; i < 7; i++) {
            if (hand[i].getSuit() == idx) {
                rcount[hand[i].getRank()]++;
            }
        }
        int high = containsStraight(rcount);
        if (high==0) { // flush
            results[0] = 5;
            int idx = 1;
            for (int i = 12; i > -1; i--) {
                if (rcount[i] > 0) {
                    results[idx] = i;
                    idx++;
                    if (idx > 6) {
                        break;
                    }
                }
            }
        } else if (high == 14) { // royal flush
            results[0] = 9;
        } else {
            results[0] = 8;
            results[1] = high;
        }
    } else {
        // no flush
        for (int i = 0; i < 7; i++) {
            rcount[hand[i].getRank()]++;
        }
        int countVals[5][2];
        highestKinds(rcount, countVals); // edits count_vals in place
        if (countVals[0][0] == 4) { // four kind
            int vals[4] = {countVals[1][1], countVals[2][1], countVals[3][1], countVals[4][1]};
            int maxima[1];
            nlargest(4,vals,1,maxima);
            results[0] = 7;
            results[1] = countVals[0][1];
            results[2] = maxima[0];
        }
        if (countVals[0][0] > 2) {
            if (countVals[1][0] > 1) { // full house
                results[0] = 6;
                results[1] = countVals[0][1];
                results[2] = countVals[1][1];
            }
            int high = containsStraight(rcount);
            if (high > 0) { // straight
                results[0] = 4;
                results[1] = high;
            }
            // three of a kind
            int vals[4] = {countVals[1][1], countVals[2][1], countVals[3][1], countVals[4][1]};
            int maxima[2];
            nlargest(4,vals,2,maxima);
            results[0] = 3;
            results[1] = countVals[0][1];
            results[2] = maxima[0];
            results[3] = maxima[1];
        }
        int high = containsStraight(rcount);
        if (high>0) { // straight
            results[0] = 4;
            results[1] = high;
        }
        if (countVals[1][0] == 2) { // two pair
            int vals[3] = {countVals[2][1], countVals[3][1], countVals[4][1]};
            int maxima[1];
            nlargest(3,vals,1,maxima);
            results[0] = 2;
            results[1] = countVals[0][1];
            results[2] = countVals[1][1];
            results[3] = maxima[0];
        }
        if (countVals[0][0] == 2) { // pair
            int vals[4] = {countVals[1][1], countVals[2][1], countVals[3][1], countVals[4][1]};
            int maxima[3];
            nlargest(4,vals,3,maxima);
            results[0] = 1;
            results[1] = countVals[0][1];
            results[2] = maxima[0];
            results[3] = maxima[1];
            results[4] = maxima[2];
        }
        // high card
        int vals[5] = {countVals[0][1], countVals[1][1], countVals[2][1], countVals[3][1], countVals[4][1]};
        int maxima[5];
        nlargest(5,vals,5,maxima);
        results[0] = 0;
        results[1] = maxima[0];
        results[2] = maxima[1];
        results[3] = maxima[2];
        results[4] = maxima[3];
        results[5] = maxima[4];
    }
}

int containsStraight(const int (&rcount)[15]) {
    bool finished;
    for (int high = 14; high > 5; high--) {
        finished = true;
        for (int run = high; run > high-5; run--) {
            if (rcount[run] == 0) {
                finished = false;
                break;
            }
        }
        if (finished) {return high;}
    }
    return 0;
}

void highestKinds(int rcount[15], int (&countVals)[5][2]) { // don't pass rcount by reference, so I can edit it
    int max;
    int idxMax;
    for (int i = 0; i < 5; i++) {
        max = -1;
        idxMax = 0;
        for (int ii = i; ii < 15; ii++) {
            if (rcount[ii] > max) {
                max = rcount[ii];
                idxMax = ii;
            }
        }
        // swap the max to be in the front
        rcount[idxMax] = rcount[i];
        rcount[i] = max;
        countVals[i][0] = max;
        countVals[i][1] = idxMax;
    }
    cout << "sorted: " << endl;
    for (int i = 0; i < 5; i++ ) {
        for (int ii = 0; ii < 2; ii++) {
            cout << countVals[i][ii] << " ";
        }
        cout << endl;
    }
}

void nlargest(int arrSize, int vals[], int num, int maxima[]) { // dont pass vals by reference, so I can edit it
    int max;
    int idxMax;
    for (int i = 0; i < num; i++) {
        max = -1;
        idxMax = 0;
        for (int ii = i; ii < arrSize; ii++) {
            if (vals[ii] > max) {
                max = vals[ii];
                idxMax = ii;
            }
        }
        vals[idxMax] = vals[i];
        vals[i] = max;
        maxima[i] = max;
    }
}