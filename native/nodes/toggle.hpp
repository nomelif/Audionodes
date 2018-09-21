
#ifndef TOGGLE_HPP
#define TOGGLE_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/trigger.hpp"
#include <cmath>

namespace audionodes {

class Toggle : public Node {
  enum InputSockets {
    trigger,
    signal_a,
    signal_b
  };
  enum OutputSockets {
    audio
  };
  enum Properties {
  };
  bool a_on = true;
  public:
  Toggle();
//  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  void process(NodeInputWindow&) override;
};

}

#endif
