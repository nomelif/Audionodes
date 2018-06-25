#include "noise.hpp"

namespace audionodes {

static NodeTypeRegistration<Noise> registration("NoiseNode");

Noise::Noise() :
    Node({SocketType::audio}, {SocketType::audio}, {}),
    distribution(-1, 1)
{
  std::random_device dev;
  generator = std::mt19937(dev());
}

void Noise::process(NodeInputWindow &input) {
  size_t n = input.get_channel_amount();
  AudioData::PolyWriter output(output_window[0], n);
  for (size_t i = 0; i < n; ++i) {
    Chunk &channel = output[i];
    const Chunk &vol = input[0][i];
    for (size_t j = 0; j < N; ++j) {
      channel[j] = distribution(generator)*vol[j];
    }
  }
}

}
