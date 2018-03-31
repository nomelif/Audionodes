
#ifndef IIR_FILTER_HPP
#define IIR_FILTER_HPP

#include "common.hpp"
#include "node.hpp"
#include "util/circular_array.hpp"

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
  static const size_t max_poles = 8;
  static const size_t max_coeff = 2*max_poles+1;
  struct Biquad {
    double a[3], b[3];
  };
  struct Coeffs {
    double a[max_coeff], b[max_coeff];
    size_t count = 1;
    Coeffs();
    // Convolve the biquad into the coefficent collection
    void apply(Biquad);
    void correct_gain(Modes);
  };
  struct Filter {
    CircularArray<double, max_coeff> in_hist, out_hist;
    Coeffs coeffs;
    bool initialized=false;
    void process(const Chunk&, Chunk&);
  };
  std::vector<Filter> bundles;
  
  public:
  IIRFilter();
  void apply_bundle_universe_changes(const Universe&);
  void process(NodeInputWindow&);
};

#endif
