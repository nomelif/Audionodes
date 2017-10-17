#!/bin/bash

g++ -O2 --std=c++14 -o native.so -fPIC -shared -lSDL2 audionodes.cpp
