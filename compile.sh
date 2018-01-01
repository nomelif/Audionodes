#!/bin/bash

# Dependencies: libsdl2-dev

if [ "$1" == "--debug" ]
then
  g++ -O2 --std=c++14 -Wall -pedantic $@ -o native.so -fPIC -shared native/*.cpp -lSDL2 -lfluidsynth -g
else
  g++ -O2 --std=c++14 -Wall -pedantic $@ -o native.so -fPIC -shared native/*.cpp -lSDL2 -lfluidsynth  -march=native
fi
