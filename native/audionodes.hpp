
#ifndef AUDIONODES_HPP
#define AUDIONODES_HPP

#include "common.hpp"
#include "node_tree.hpp"

#include <iostream>
#include <map>
#include <mutex>
#include <functional>
#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>

typedef std::function<Node*()> NodeCreator;
#define NodeType(type, ident) {(ident), ([](){ return (Node*)new type(); })}

#endif
