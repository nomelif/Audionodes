#include "random_access_delay.hpp"

namespace audionodes {

static NodeTypeRegistration<RandomAccessDelay> registration("RandomAccessDelayNode");

RandomAccessDelay::RandomAccessDelay() :
    Node(SocketTypeList(3, SocketType::audio), {SocketType::audio}, {PropertyType::number})
{}

void RandomAccessDelay::apply_bundle_universe_changes(const Universe &universe) {
  universe.apply_delta(bundles);
}

void RandomAccessDelay::process(NodeInputWindow &input) {
  size_t n = input.get_channel_amount();
  AudioData::PolyWriter output(output_window[0], n);
  
  // Ugh, float properties not supported yet
  const size_t buffer_size =
    std::max(4096, get_property_value(Properties::buffer_size)*RATE);
  for (size_t i = 0; i < n; ++i) {
    const Chunk
      &signal = input[InputSockets::signal][i],
      &delay_time = input[InputSockets::delay_time][i],
      &feedback = input[InputSockets::feedback][i];
    Chunk &chunk = output[i];
    auto &bundle = bundles[i];
    bundle.resize(buffer_size);
    for (size_t j = 0; j < N; ++j) {
      SigT time = std::floor(delay_time[j]*RATE);
      if (time < 1) time = 1;
      if (time > buffer_size-2) time = buffer_size-2;
      size_t samples = time;
      size_t idx1 = bundle.write_head;
      if (samples > idx1) idx1 += buffer_size;
      idx1 -= samples;
      size_t idx2 = idx1;
      if (idx2 == 0) idx2 = buffer_size;
      idx2--;
      SigT v1 = bundle.buffer[idx1], v2 = bundle.buffer[idx2];
      // Linear interpolation
      chunk[j] = v1+std::fmod(delay_time[j]*RATE, 1)*(v2-v1);
      if (!std::isfinite(chunk[j])) chunk[j] = 0;
      SigT fbval = signal[j]+chunk[j]*feedback[j];
      bundle.buffer[bundle.write_head] = fbval;
      bundle.write_head++;
      if (bundle.write_head == buffer_size) bundle.write_head = 0;
    }
  }
}

void RandomAccessDelay::Bundle::resize(size_t size) {
  if (size != buffer.size()) {
    buffer.resize(size);
    write_head %= size;
  }
}

}
