
#ifndef SAMPLER_HPP
#define SAMPLER_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include "data/trigger.hpp"
#include <cmath>

class Sampler : public Node {
  enum InputSockets {
    midi_in
  };
  enum OutputSockets {
    trigger
  };
  enum Properties {
  };


  Uint16* buff = nullptr;
  size_t size;
  bool loaded = false;


  public:
  Sampler();
  ~Sampler();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  void process(NodeInputWindow&);
  void receive_binary(int, int, void*);
};
#endif
