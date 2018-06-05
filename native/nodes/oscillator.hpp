
#ifndef OSCILLATOR_HPP
#define OSCILLATOR_HPP

#include "common.hpp"
#include "node.hpp"
#include <functional>

namespace audionodes {

class Oscillator : public Node {
  enum InputSockets {
    frequency, amplitude, offset, param
  };
  enum Properties {
    oscillation_func, anti_alias
  };
  enum Modes {
    sine, saw, square, triangle
  };
  
  // Persistent state
  struct Bundle {
    SigT state, last_val;
  };
  std::vector<Bundle> bundles;

  static SigT poly_blep(SigT, SigT);
  public:
  Oscillator();
  void reset_state();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  void apply_bundle_universe_changes(const Universe&);
  void process(NodeInputWindow&);
};

}

#endif
