
#ifndef PITCH_BEND_HPP
#define PITCH_BEND_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include <cmath>

namespace audionodes {

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
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>) override;
  void process(NodeInputWindow&) override;
};

}

#endif
