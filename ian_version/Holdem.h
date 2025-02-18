#ifndef HOLDEM_H
#define HOLDEM_H

#include<vector>
#include<string>

using namespace std;

enum Play {NULL_PLAY, CALL, RAISE, FOLD};

class Player { // Parent class for ComputerPlayer and HumanPlayer to avoid redundancy
  protected:
    string const name;
    unsigned int money = -1; // The negative one is for testing only. Remove before implementation

  public:
    // Player(string name) : name(name) {}
    // Player(string name, unsigned int money) : name(name), money(money) {}
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
  public:
    HumanPlayer(string name, unsigned int money) : name(name), money(money) {}
    Play takeTurn() {

    }
};

class Seat {
  private:
    const Player* player;
    unsigned int money;
    unsigned int bid = 0;

  public:
    Seat(Player* player, unsigned int buyInFee) : player(player), money(buyInFee) { player->pay(buyInFee); }
};

class Table {
  private:
    unsigned int buyInFee;
    vector<Seat> seats;
    unsigned int bid;

  public:
    Table(vector<Player*> players, unsigned int buyInFee) : buyInFee(buyInFee) {
      for (Player* player : players) {
        seats.push_back(Seat(player, buyInFee));
      }
    }
}

#endif
