
#ifndef PITCH_BEND_HPP
#define PITCH_BEND_HPP

#include "common.hpp"
#include "node.hpp"
#include "midi_data.hpp"
#include <cmath>

class PitchBend : public Node {
  enum InputSockets {
    midi_in
  };
  enum OutputSockets {
    bend
  };
  SigT bend_state;
  public:
  PitchBend();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  NodeOutputWindow process(NodeInputWindow&);
};

#endif
