#ifndef HOLDEM_H
#define HOLDEM_H

#include <vector>
#include <string>
#include <exception>
#include "Cards.h"

using namespace std;

enum Play {NULL_PLAY, CALL, RAISE, FOLD};

class Player { // Parent class for ComputerPlayer and HumanPlayer to avoid redundancy
  protected:
    string const name;
    unsigned int money = -1; // FIXME: The negative one is for testing only. Remove before implementation

  public:
    string getName() { return name; }
    void pay(unsigned int amount) { money -= amount; }
    void earn(unsigned int amount) { money += amount; }
};

class ComputerPlayer : public Player { // FIXME: figure out what data to pass to doTurn/takeTurn
  private:
    function<Play()> const doTurn;
  public:
    ComputerPlayer(string name, unsigned int money, function<Play()>& doTurn) : name(name), money(money), doTurn(doTurn) {}
    Play takeTurn() { return doTurn(); }
};

class HumanPlayer : public Player {
  private:
    // int const userKey; // May implement unique user keys if implementing repeatable play. Would need new constructor
  public:
    HumanPlayer(string name, unsigned int money) : name(name), money(money) {}
    Play takeTurn() {
      // FIXME: Implement
    }
};

class Seat {
  private:
    Player* const player;
    Card* hand[2];
    unsigned int money;
    unsigned int bid = 0;
    bool hasFolded = false;

    Seat* nextPlayer;
    Seat* prevPlayer;

  public:
    Seat(Player* player, unsigned int buyInFee) : player(player), money(buyInFee) { player->pay(buyInFee); }

    Seat* next() { return nextPlayer; }
    Seat* prev() { return prevPlayer; }
    void setNext(Seat* next) { nextPlayer = next; }
    void setPrev(Seat* previous) { prevPlayer = previous; }

    void takeTurn() { // FIXME: Figure out what data needs to be passed in
      Play play = player->takeTurn();
      switch (play) { // FIXME: Implement
        case CALL:
          break;
        case RAISE:
          break;
        case FOLD:
          break;
        default:
          // FIXME: Implement error catching
      }
    }
};

class Table {
  private:
    unsigned int buyInFee;
    unsigned int blindSize; // Small bline size
    unsigned int currBid = 0;
    unsigned int pot = 0;

    Seat* bigBlind;
    Seat* smallBlind;
    Seat* currPlayer;

    Deck deck;
    Card* board[5];

  public:
    Table(vector<Player*> players, unsigned int buyInFee, unsigned int startingSmallBlind) : buyInFee(buyInFee), blindSize(startingSmallBlind) {
      for (Player* player : players) {
        int size = players.size();
        if (size < 2) { throw length_error("Error: Cannot play poker with fewer than 2 players"); }
        smallBlind = new Seat(players.at(0), buyInFee);
        bigBlind = new Seat(players.at(1), buyInFee);
        smallBlind->setNext(bigBlind);
        bigBlind->setPrev(smallBlind);
        Seat* currSeat = bigBlind;
        Seat* nextSeat;
        for (int i = 2; i < size; ++i) {
          nextSeat = new Seat(players.at(i), buyInFee));
          currSeat->setNext(nextSeat);
          nextSeat->setPrev(currSeat);
          currSeat = nextSeat;
        }
        currSeat->setNext(smallBlind);
        smallBlind->setPrev(currSeat);
      }
    }
    ~Table() {
      Seat* currSeat = smallBlind;
      smallBlind->prev()->setNext(nullPtr);
      Seat* nextSeat;
      while(currSeat != nullPtr) {
        nextSeat = currSeat->next();
        delete currSeat;
        currSeat = nextSeat;
      }
      void eliminate(Seat* seat) {
        seat->prev()->setNext(seat->next());
        seat->next()->setPrev(seat->prev());
        delete seat;
      }
    }

}

#endif
