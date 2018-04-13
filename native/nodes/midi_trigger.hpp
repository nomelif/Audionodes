
#ifndef MIDI_TRIGGER_HPP
#define MIDI_TRIGGER_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include "data/trigger.hpp"
#include <cmath>

class MidiTrigger : public Node {
  enum InputSockets {
    midi_in
  };
  enum OutputSockets {
    trigger
  };
  enum Properties {
    channel,
    interfaceType
  };
  public:
  MidiTrigger();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  void process(NodeInputWindow&);
};

#endif
