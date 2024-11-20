#ifndef CARDS_H
#define CARDS_H

#include <string>
#include <vector>

using namespace std;

enum Rank { TWO = 2, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE };
enum Suit { DIAMONDS, CLUBS, HEARTS, SPADES };

class Card {
  private:
    Rank rank;
    Suit suit;

  public:
    Card(Rank rank, Suit suit) : rank(rank), suit(suit) {}
    Card(int rank, int suit) : rank(static_cast<Rank>(rank)), suit(static_cast<Suit>(suit)) {}
    Card(Rank rank, int suit) : rank(rank), suit(static_cast<Suit>(suit)) {}
    Card(int rank, Suit suit) : rank(static_cast<Rank>(rank)), suit(suit) {}
    Card(string cardName) {
      switch (cardName[cardName.size()-1]) {
        case 'd': suit = DIAMONDS; break;
        case 'c': suit = CLUBS; break;
        case 'h': suit = HEARTS; break;
        case 's': suit = SPADES; break;
        default: break; // FIXME: add error handling
      }
      cardName.pop_back();
      if (cardName == "j") { rank = JACK; }
      else if (cardName == "q") { rank = QUEEN; }
      else if (cardName == "k") { rank = KING; }
      else if (cardName == "a") { rank = ACE; }
      else if ( 1 < stoi(cardName) && stoi(cardName) < 11) { rank = static_cast<Rank>(stoi(cardName)); }
      else {} // FIXME: add error handling
    }

    Rank getRank() const { return rank; }

    Suit getSuit() const { return suit; }

    Card& operator=(const Card &other) {
      rank = other.rank;
      suit = other.suit;
      return *this;
    }

    friend bool operator<(const Card &card1, const Card &card2) {
      return card1.rank < card2.rank || (card1.rank == card2.rank && card1.suit < card2.suit);
    }

    friend bool operator>(const Card &card1, const Card &card2) {
      return card2 < card1;
    }

    friend bool operator==(const Card &card1, const Card &card2) {
      return card1.rank == card2.rank && card1.suit == card2.suit;
    }

    friend bool operator<=(const Card &card1, const Card &card2) {
      return card1 < card2 || card1 == card2;
    }

    friend bool operator>=(const Card &card1, const Card &card2) {
      return card2 < card1 || card1 == card2;
    }
};

class Deck {
    private:
    vector<Card*> cards;

    public:
      Deck() {
        for (int suit = 0; suit < 4; suit++) {
          for (int rank = 2; rank < 14; rank++) {
            cards.push_back(new Card(rank, suit));
          }
        }
      }
      ~Deck() {
        for (int i = 0; i < 52; i++) {
          delete cards[i];
          cards[i] = nullptr;
        }
      }
};

#endif