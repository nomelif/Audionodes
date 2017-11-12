#!/bin/bash

# Dependencies: libsdl2-dev

g++ -O2 --std=c++14 -Wall -o native.so -fPIC -shared native/*.cpp -lSDL2
