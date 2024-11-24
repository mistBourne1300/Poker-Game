#ifndef CARDS_H
#define CARDS_H

// #include <iostream> // TODO: delete this line when done with testing
#include <string>
#include <sstream>
#include <vector>
#include <exception>
#include <random>

using namespace std;

enum Rank { NULL_RANK = 0, TWO=2, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE, RANK_COUNT };
enum Suit { NULL_SUIT = 0, DIAMONDS, CLUBS, HEARTS, SPADES, SUIT_COUNT };
enum HandType { NULL_HAND = 0, HIGH_CARD, PAIR, TWO_PAIR, THREE_OF_A_KIND, STRAIGHT, FLUSH, FULL_HOUSE, FOUR_OF_A_KIND, STRAIGHT_FLUSH, ROYAL_FLUSH, HAND_COUNT };
inline Rank& operator++(Rank &rank) {
  rank = static_cast<Rank>((static_cast<int>(rank) + 1));
  return rank;
}
inline Rank operator++(Rank &rank, int) {
  Rank r = rank;
  ++rank;
  return r;
}
inline Suit& operator++(Suit &suit) {
  suit = static_cast<Suit>((static_cast<int>(suit) + 1));
  return suit;
}
inline Suit operator++(Suit &suit, int) {
  Suit s = suit;
  ++suit;
  return s;
}

class Card {
    Rank rank;
    Suit suit;

  public:
    Card() : rank(NULL_RANK), suit(NULL_SUIT) {}
    Card(Rank rank, Suit suit) : rank(rank), suit(suit) {}
    Card(int rank, int suit) : rank(static_cast<Rank>(rank)), suit(static_cast<Suit>(suit)) {}
    Card(Rank rank, int suit) : rank(rank), suit(static_cast<Suit>(suit)) {}
    Card(int rank, Suit suit) : rank(static_cast<Rank>(rank)), suit(suit) {}
    explicit Card(string cardName) {
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

    Card& operator=(const Card &other) = default;

    string toString() const {
      stringstream ss;
      ss << "[";
      switch (rank) {
        case ACE: ss << "a"; break;
        case KING: ss << "k"; break;
        case QUEEN: ss << "q"; break;
        case JACK: ss << "j"; break;
        case TEN: ss << "10"; break;
        case NINE: ss << "9"; break;
        case EIGHT: ss << "8"; break;
        case SEVEN: ss << "7"; break;
        case SIX: ss << "6"; break;
        case FIVE: ss << "5"; break;
        case FOUR: ss << "4"; break;
        case THREE: ss << "3"; break;
        case TWO: ss << "2"; break;
        default:
          stringstream ee;
          ee << "Invalid card rank: " << rank;
          throw ee.str();
      }
      switch (suit) {
        case SPADES: ss << "s"; break;
        case HEARTS: ss << "h"; break;
        case CLUBS: ss << "c"; break;
        case DIAMONDS: ss << "d"; break;
        default:
          stringstream ee;
          ee << "Invalid card suit: " << suit;
          throw ee.str();
      }
      ss << "]";
      return ss.str();
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

   friend bool operator!=(const Card &card1, const Card &card2) {
      return !(card1 == card2);
    }

    friend bool operator<=(const Card &card1, const Card &card2) {
      return card1 < card2 || card1 == card2;
    }

    friend bool operator>=(const Card &card1, const Card &card2) {
      return card2 < card1 || card1 == card2;
    }
};

class Hand {
    HandType type;
    Card cards[5];

  public:
    Hand(HandType hand_type, vector<Card> inCards) : type(hand_type) {
      if (inCards.size() < 5) {throw length_error("Can't initialize hand with fewer than 5 cards"); }
      if (inCards.size() > 5) {throw length_error("Can't initialize hand with more than 5 cards"); }
      for (int i = 0; i < 5; i++) {
        cards[i] = inCards.at(i);
      }
    }
    Hand(int hand_type, vector<Card> inCards) : type(static_cast<HandType>(hand_type)) {
      if (inCards.size() < 5) {throw length_error("Can't initialize hand with fewer than 5 cards"); }
      if (inCards.size() > 5) {throw length_error("Can't initialize hand with more than 5 cards"); }
      for (int i = 0; i < 5; i++) {
        cards[i] = inCards.at(i);
      }
    }

    Card at(unsigned int index) const { return cards[index]; }
    HandType getType() const { return type; }

    friend bool operator<(const Hand &hand1, const Hand &hand2) {
      if (hand1.type != hand2.type) { return hand1.type < hand2.type; }
      for (int i = 0; i < 5; i++) {
        if (hand1.at(i).getRank() != hand2.at(i).getRank()) { return hand1.at(i).getRank() < hand2.at(i).getRank(); }
      }
      return false;
    }

    friend bool operator>(const Hand &hand1, const Hand &hand2) {
      return hand2 < hand1;
    }

    friend bool operator==(const Hand &hand1, const Hand &hand2) {
      if (hand1.type != hand2.type) { return false; }
      for (int i = 0; i < 5; i++) {
        if (hand1.at(i).getRank() != hand2.at(i).getRank()) { return false; }
      }
      return true;
    }

    friend bool operator!=(const Hand &hand1, const Hand &hand2) {
      return !(hand1 == hand2);
    }

    friend bool operator<=(const Hand &hand1, const Hand &hand2) {
      return hand1 < hand2 || hand1 == hand2;
    }

    friend bool operator>=(const Hand &hand1, const Hand &hand2) {
      return hand2 < hand1 || hand1 == hand2;
    }

};

class Deck {
    vector<Card*> cards;
    int next_deal = 0;

  public:
    Deck() {
      for (Suit suit = DIAMONDS; suit < SUIT_COUNT; ++suit) {
        for (Rank rank = TWO; rank < RANK_COUNT; ++rank) {
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

    Card* deal() {
      return cards.at(next_deal++);
      // FIXME: add error checking in case there are no cards left
    }

    void shuffle() {
      next_deal = 0;
      random_device rd;
      mt19937 gen(rd());
      for (int i = 0; i < 51; i++) {
        uniform_int_distribution<> dis(i, 51);
        swap(cards[i],cards[dis(gen)]);
       }
    }
};

#endif