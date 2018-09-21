
#ifndef OSCILLATOR_HPP
#define OSCILLATOR_HPP

#include "common.hpp"
#include "node.hpp"
#include <functional>

namespace audionodes {

class Oscillator : public Node {
  enum InputSockets {
    frequency, amplitude, offset, phase, param
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
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>) override;
  void apply_bundle_universe_changes(const Universe&) override;
  void process(NodeInputWindow&) override;
};

}

#endif
