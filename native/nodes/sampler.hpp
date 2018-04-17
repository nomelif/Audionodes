
#ifndef SAMPLER_HPP
#define SAMPLER_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include "data/trigger.hpp"
#include <cmath>
#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>

class Sampler : public Node {
  enum InputSockets {
    trigger_socket
  };
  enum OutputSockets {
    audio_socket
  };
  enum Properties {
  };


  SigT* buff = nullptr;
  size_t size;
  size_t playhead = -1;
  bool loaded = false;
  std::mutex wav_lock;


  public:
  Sampler();
  ~Sampler();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  void process(NodeInputWindow&);
  void receive_binary(int, int, void*);
};
#endif
