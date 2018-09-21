
#ifndef IIR_FILTER_HPP
#define IIR_FILTER_HPP

#include "common.hpp"
#include "node.hpp"

namespace audionodes {

class IIRFilter : public Node {
  enum InputSockets {
    input, cutoff, resonance, rolloff
  };
  enum Properties {
    mode, poles
  };
  enum Modes {
    low_pass, high_pass
  };
  static const size_t max_poles = 6;
  typedef double FSigT;
  struct DirectForm {
    FSigT a[3], b[3];
    void correct_gain(Modes);
  };
  struct Lattice {
    FSigT k[2], v[3];
    FSigT state[2];
    static Lattice interpolate(const Lattice&, const Lattice&, FSigT);
  };
  struct Filter {
    Lattice biquads[max_poles];
    Lattice old_biquads[max_poles];
    Modes mode;
    size_t poles;
    SigT cutoff, resonance, rolloff;
    bool initialized = false;
    Filter() = default;
    Filter(Modes, size_t, SigT, SigT, SigT);
    bool equivalent(Modes, size_t, SigT, SigT, SigT) const;
    void copy_state(const Filter&);
    void process(const Chunk&, Chunk&, bool);
  };
  std::vector<Filter> bundles;
  
  public:
  IIRFilter();
  void apply_bundle_universe_changes(const Universe&) override;
  void process(NodeInputWindow&) override;
};

}

#endif
