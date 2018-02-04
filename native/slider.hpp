
#ifndef SLIDER_HPP
#define SLIDER_HPP

#include "common.hpp"
#include "node.hpp"
#include "midi_data.hpp"
#include <cmath>

class Slider : public Node {
  enum InputSockets {
    midi_in
  };
  enum OutputSockets {
    value
  };
  enum Properties {
    channel
  };
  SigT value_state;
  public:
  Slider();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  NodeOutputWindow process(NodeInputWindow&);
};

#endif
