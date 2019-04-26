#ifndef TRIGGER_ENVELOPE_HPP
#define TRIGGER_ENVELOPE_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/trigger.hpp"
#include <cmath>

namespace audionodes {

class TriggerEnvelope : public Node {
  enum InputSockets {
    trigger,
    delay_time,
    attack_time,
    hold_time,
    hold_level,
    attack_slope,
    decay_slope,
    release_slope
  };
  enum OutputSockets {
    envelope
  };
  
  enum class Phase {
    released,
    waiting,
    attack,
    hold
  } current_phase = Phase::released;
  long time_elapsed = 0;
  SigT current_state = 0;
  
  public:
  TriggerEnvelope();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>) override;
  void process(NodeInputWindow&) override;
};

}

#endif
