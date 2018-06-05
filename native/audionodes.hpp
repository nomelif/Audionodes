
#ifndef AUDIONODES_HPP
#define AUDIONODES_HPP

#include "common.hpp"
#include "node_tree.hpp"
#include "util/circular_buffer.hpp"

#include <iostream>
#include <map>
#include <set>
#include <mutex>
#include <functional>
#include <thread>
#include <cstring>
#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>

namespace audionodes {

struct Message {
  enum class Type {
    audio_input, property, binary    
  };
  Type type;
  Node *node;
  size_t slot;
  
  float audio_input;
  int property;
  void *binary;
  
  void apply();
  
  Message();
  Message(Node*, size_t, float);
  Message(Node*, size_t, int);
  Message(Node*, size_t, int, void*);
};

typedef std::function<Node*()> NodeCreator;
#define NodeType(type, ident) {(ident), ([](){ return (Node*)new type(); })}

}

#endif
