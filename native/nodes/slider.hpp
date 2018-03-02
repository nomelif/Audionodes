
#ifndef SLIDER_HPP
#define SLIDER_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include <cmath>

class Slider : public Node {
  enum InputSockets {
    midi_in
  };
  enum OutputSockets {
    value
  };
  enum Properties {
    channel,
    interfaceType
  };
  SigT value_state;
  public:
  Slider();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  void process(NodeInputWindow&);
};

#endif
