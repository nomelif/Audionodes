
#ifndef SINE_OSCILLATOR_HPP
#define SINE_OSCILLATOR_HPP

#include "common.hpp"
#include "node.hpp"

class SineOscillator : public Node {
  float state;
  enum InputSocket {
    frequency, amplitude, offset
  };
  public:
  const static int type_id = 0;
  SineOscillator();
  void resetState();
  std::vector<Chunk> process(std::vector<Chunk>);
};

#endif
