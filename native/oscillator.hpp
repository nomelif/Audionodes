
#ifndef OSCILLATOR_HPP
#define OSCILLATOR_HPP

#include "common.hpp"
#include "node.hpp"
#include <functional>

class Oscillator : public Node {
  SigT state;
  enum InputSockets {
    frequency, amplitude, offset, param
  };
  enum Properties {
    oscillation_func
  };
  typedef std::function<SigT(SigT, SigT)> OscillationFuncType;
  typedef std::vector<OscillationFuncType> OscillationFuncListType;
  const static OscillationFuncListType oscillation_funcs;
  public:
  const static int type_id = 0;
  Oscillator();
  void reset_state();
  std::vector<Chunk> process(std::vector<Chunk>);
};

#endif
