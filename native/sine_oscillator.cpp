#include "sine_oscillator.hpp"

SineOscillator::SineOscillator() :
    Node(3, 1),
    state(0.)
{}

void SineOscillator::resetState() {
  state = 0.;
}

std::vector<Chunk> SineOscillator::process(std::vector<Chunk> input) {
  auto output = std::vector<Chunk>(1, Chunk());
  for (size_t i = 0; i < N; ++i) {
    state = std::fmod(state + input[InputSocket::frequency][i]/rate, 1);
    output[0][i] =
      std::sin(state*2*M_PI) * input[InputSocket::amplitude][i]
      + input[InputSocket::offset][i];
  }
  return output;
}

