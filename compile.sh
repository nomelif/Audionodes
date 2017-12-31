#!/bin/bash

# Dependencies: libsdl2-dev

if [ "$1" == "--debug" ]
then
  g++ -O2 --std=c++14 -Wall -pedantic $@ -o native.so -fPIC -shared native/*.cpp -lSDL2 -g
else
  g++ -O2 --std=c++14 -Wall -pedantic $@ -o native.so -fPIC -shared native/*.cpp -lSDL2 -march=native
fi
