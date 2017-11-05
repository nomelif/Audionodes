#include "oscillator.hpp"


Oscillator::Oscillator() :
    Node(4, 1, 1),
    state(0.)
{}

void Oscillator::reset_state() {
  state = 0.;
}

const Oscillator::OscillationFuncListType Oscillator::oscillation_funcs = {
  // 0: Sine
  [](SigT phase, SigT) { return std::sin(phase*2*M_PI); },
  // 1: Saw
  [](SigT phase, SigT) { return phase * 2 - 1; },
  // 2: Square (param pulse_width)
  [](SigT phase, SigT pulse_width) { return phase > 1-pulse_width ? 1. : -1.; },
  // 3: Triangle
  [](SigT phase, SigT) { return std::fabs(phase * 4 - 2) - 1; }
};

std::vector<Chunk> Oscillator::process(std::vector<Chunk> input) {
  auto output = std::vector<Chunk>(1, Chunk());
  const OscillationFuncType &func =
    oscillation_funcs[get_property_value(Properties::oscillation_func)];
  for (size_t i = 0; i < N; ++i) {
    state = std::fmod(state + input[InputSockets::frequency][i]/rate, 1);
    output[0][i] =
      func(state, input[InputSockets::param][i]) * input[InputSockets::amplitude][i]
      + input[InputSockets::offset][i];
  }
  return output;
}

