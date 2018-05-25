
#ifndef MICROPHONE_HPP
#define MICROPHONE_HPP

#include "common.hpp"
#include "node.hpp"
#include "util/circular_buffer.hpp"

#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>

class Microphone : public Node {
  SDL_AudioDeviceID dev = 0;
  CircularBuffer<SigT, 4096> q;
  static void callback(void*, Uint8*, int);
  public:
  Microphone();
  ~Microphone();
  void connect_callback();
  void process(NodeInputWindow&);
};

#endif
