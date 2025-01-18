#!/bin/bash

cd $HOME/Desktop/Poker-Game
source .venv/bin/activate
cd poker_game
python3 genetic_expector_training.py
systemctl suspend