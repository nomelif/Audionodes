
#ifndef SLIDER_HPP
#define SLIDER_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include <cmath>

namespace audionodes {

class MIDIControl : public Node {
  enum InputSockets {
    midi_in
  };
  enum OutputSockets {
    value
  };
  enum Properties {
    channel,
    cc_no
  };
  SigT value_state;
  public:
  MIDIControl();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>) override;
  void process(NodeInputWindow&) override;
};

}

#endif
