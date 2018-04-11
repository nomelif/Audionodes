
#ifndef TRIGGER_HPP
#define TRIGGER_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include "data/trigger.hpp"
#include <cmath>

class Trigger : public Node {
  enum InputSockets {
    midi_in
  };
  enum OutputSockets {
    trigger
  };
  enum Properties {
    channel
  };
  public:
  Trigger();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  void process(NodeInputWindow&);
};

#endif
