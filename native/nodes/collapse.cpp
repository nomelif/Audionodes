#include "nodes/collapse.hpp"
#include <limits>

namespace audionodes {

static NodeTypeRegistration<Collapse> registration("CollapseNode");

Collapse::Collapse() :
  Node({SocketType::audio}, {SocketType::audio}, {PropertyType::select})
{}

Universe::Descriptor Collapse::infer_polyphony_operation(std::vector<Universe::Pointer> inputs) {
  Universe::Pointer mono(new Universe());
  return Universe::Descriptor(inputs[0], mono, mono);
}

void Collapse::process(NodeInputWindow &input) {
  size_t n = input.universes.input->get_channel_amount();
  Chunk &output = output_window[OutputSockets::audio_out].mono;
  switch (get_property_value(Properties::flatten_method)) {
    typedef FlattenMethods FM;
    case FM::sum:
      output.fill(0);
      for (size_t i = 0; i < n; ++i) {
        const Chunk &input_chunk = input[0][i];
        for (size_t j = 0; j < N; ++j) {
          output[j] += input_chunk[j];
        }
      }
      break;
    case FM::maximum:
      output.fill(-std::numeric_limits<SigT>::infinity());
      for (size_t i = 0; i < n; ++i) {
        const Chunk &input_chunk = input[0][i];
        for (size_t j = 0; j < N; ++j) {
          output[j] = std::max(output[j], input_chunk[j]);
        }
      }
      break;
    case FM::minimum:
      output.fill(std::numeric_limits<SigT>::infinity());
      for (size_t i = 0; i < n; ++i) {
        const Chunk &input_chunk = input[0][i];
        for (size_t j = 0; j < N; ++j) {
          output[j] = std::min(output[j], input_chunk[j]);
        }
      }
      break;
    case FM::product:
      output.fill(1);
      for (size_t i = 0; i < n; ++i) {
        const Chunk &input_chunk = input[0][i];
        for (size_t j = 0; j < N; ++j) {
          output[j] *= input_chunk[j];
        }
      }
      break;
  }
}

}
