#!/bin/bash

# Dependencies: sdl2, fluidsynth

# Ubuntu: sudo apt install libsdl2-dev libfluidsynth-dev
# Arch Linux: sudo pacman -S sdl2 fluidsynth
# MacOS: brew install sdl2 fluidsynth

if [ "$1" == "--debug" ]
then
  g++ --std=c++14 -Wall -pedantic $@ -o native.so -fPIC -shared native/*.cpp -lSDL2 -lfluidsynth -g
else
  g++ -O2 --std=c++14 -Wall -pedantic $@ -o native.so -fPIC -shared native/*.cpp -lSDL2 -lfluidsynth
fi
