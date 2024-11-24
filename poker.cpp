#include <iostream>
#include <vector>
#include "cards.h"

using namespace std;

int main(int argc, char* argv) {
    Deck deck;
    for (int j = 0; j < 4; ++j) {
        for (int i = 0; i < 13; ++i) { cout << deck.deal()->toString() << " "; }
        cout << endl;
    }
    cout << endl;
    deck.shuffle();
    for (int j = 0; j < 4; ++j) {
        for (int i = 0; i < 13; ++i) { cout << deck.deal()->toString() << " "; }
        cout << endl;
    }

    return 0;
}