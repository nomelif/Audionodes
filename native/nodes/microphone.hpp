
#ifndef MICROPHONE_HPP
#define MICROPHONE_HPP

#include "common.hpp"
#include "node.hpp"
#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>
#include <queue>

class Microphone : public Node {
  public:
  Microphone();
  std::queue<SigT> q;
  void process(NodeInputWindow&);
};

#endif
