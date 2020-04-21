
#ifndef AUDIONODES_HPP
#define AUDIONODES_HPP

#include "common.hpp"
#include "node_tree.hpp"
#include "util/circular_buffer.hpp"
#include "node.hpp"

extern "C" {
#include "c_interface.h"
}

#include <iostream>
#include <map>
#include <set>
#include <atomic>
#include <mutex>
#include <thread>
#include <cstring>
#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>

namespace audionodes {

struct InboundMessage {
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
  
  InboundMessage();
  InboundMessage(Node*, size_t, float);
  InboundMessage(Node*, size_t, int);
  InboundMessage(Node*, size_t, int, void*);
};

typedef std::map<std::string, Node::Creator> NodeTypeMap;

}

#endif
