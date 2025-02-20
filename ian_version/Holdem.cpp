#include <iostream>
#include <random>
#include "Cards.h"

using namespace std;

int main(const int argc, const char* argv[]) {
  Deck deck;
  for (int i = 0; i < 52; ++i) {
    cout << deck.deal()->toString() << " ";
  }
  cout << endl << endl;
  deck.shuffle();
  for (int i = 0; i < 52; ++i) {
    cout << deck.deal()->toString() << " ";
  }
  return 0;
}
