#ifndef POKER_H
#define POKER_H

#include "cards.h"

enum Play { CALL, RAISE, FOLD, NUM_PLAYS };

class Player {
  vector<Card*> hand = {nullptr, nullptr};

  public:
    void clearHand() {
      hand.at(0) = nullptr;
      hand.at(1) = nullptr;
    }

    vector<Card*> getHand() { return hand; }

    Play takeTurn();
};

class PC : Player {};

class NPC : Player {};

class Table {
  vector<Card*> board;
  vector<Player> players;
};

#endif