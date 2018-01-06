#include "oscillator.hpp"


Oscillator::Oscillator() :
    Node(
      SocketTypeList(4, SocketType::audio),
      {SocketType::audio},
      {PropertyType::select}
    )
{}

void Oscillator::reset_state() {
  for (SigT &state : bundles) {
    state = 0;
  }
}

const Oscillator::OscillationFuncList Oscillator::oscillation_funcs = {
  // 0: Sine
  [](SigT phase, SigT) { return std::sin(phase*2*M_PI); },
  // 1: Saw
  [](SigT phase, SigT) { return phase * 2 - 1; },
  // 2: Square (param pulse_width)
  [](SigT phase, SigT pulse_width) { return phase > 1-pulse_width ? 1. : -1.; },
  // 3: Triangle
  [](SigT phase, SigT) { return std::fabs(phase * 4 - 2) - 1; }
};

Universe::Descriptor Oscillator::infer_polyphony_operation(std::vector<Universe::Pointer> inputs) {
  Universe::Descriptor result;
  // Prioritize frequency input
  if (inputs[InputSockets::frequency]->is_polyphonic()) {
    result.set_all(inputs[InputSockets::frequency]);
  } else {
    result.bundles = inputs[InputSockets::frequency];
    for (auto uni : inputs) {
      if (uni->is_polyphonic()) {
        result.input = uni;
        result.output = uni;
        break;
      }
    }
  }
  return result;
}

void Oscillator::apply_bundle_universe_changes(const Universe &universe) {
  universe.apply_delta(bundles);
}

NodeOutputWindow Oscillator::process(NodeInputWindow &input) {
  size_t n = input.get_channel_amount();
  AudioData::PolyList output(n);
  const OscillationFunc &func =
    oscillation_funcs[get_property_value(Properties::oscillation_func)];
  
  bool frequency_is_poly = input.universes.bundles->is_polyphonic();
  AudioData::PolyList states(bundles.size());
  for (size_t i = 0; i < bundles.size(); ++i) {
    const Chunk &frequency = input[InputSockets::frequency][i];
    SigT state = bundles[i];
    Chunk &channel = states[i];
    for (size_t j = 0; j < N; ++j) {
      state = std::fmod(state + frequency[j]/rate, 1);
      channel[j] = state;
    }
    bundles[i] = state;
  }
  for (size_t i = 0; i < n; ++i) {
    const Chunk
      &state = states[frequency_is_poly ? i : 0],
      &amplitude = input[InputSockets::amplitude][i],
      &offset    = input[InputSockets::offset][i],
      &param     = input[InputSockets::param][i];
    Chunk &channel = output[i];
    for (size_t j = 0; j < N; ++j) {
      channel[j] = func(state[j], param[j]) * amplitude[j] + offset[j];
    }
  }
  return NodeOutputWindow({new AudioData(output)});
}

