#ifndef CLOCK_HPP
#define CLOCK_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/trigger.hpp"
#include <cmath>

namespace audionodes {

class Clock : public Node {
  enum InputSockets {
    rate,
    run_stop
  };
  enum OutputSockets {
    trigger
  };
  bool running = true;
  double time_since_tick = 0;
  bool tick_now = true;
  public:
  Clock();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>) override;
  void process(NodeInputWindow&) override;
};

}

#endif
