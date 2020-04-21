
#ifndef SAMPLER_HPP
#define SAMPLER_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include "data/trigger.hpp"
#include <cmath>
#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>

namespace audionodes {

class Sampler : public Node {
  enum InputSockets {
    trigger_socket
  };
  enum OutputSockets {
    audio_socket
  };
  enum Properties {
    mode
  };
  enum Modes {
    oneshot,
    loop
  };
  
  std::vector<float> buff;
  size_t size;
  size_t playhead = 0;
  bool running = false;
  bool loaded = false;
  
  public:
  Sampler();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>) override;
  void process(NodeInputWindow&) override;
  void receive_binary(int, int, void*) override;
};
}

#endif
