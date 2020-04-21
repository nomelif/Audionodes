#ifndef TRIGGER_SEQUENCER_HPP
#define TRIGGER_SEQUENCER_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/trigger.hpp"

namespace audionodes {

class TriggerSequencer : public Node {
  const static size_t max_steps = 128;
  size_t step_count;
  bool active[max_steps];
  
  size_t current_step = 0;
  size_t ui_current_step;
  public:
  TriggerSequencer();
  void receive_binary(int, int, void*) override;
  void process(NodeInputWindow&) override;
};

}

#endif
