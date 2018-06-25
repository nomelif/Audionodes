#include "nodes/oscillator.hpp"

namespace audionodes {

static NodeTypeRegistration<Oscillator> registration("OscillatorNode");

Oscillator::Oscillator() :
    Node(
      SocketTypeList(4, SocketType::audio),
      {SocketType::audio},
      {PropertyType::select, PropertyType::boolean}
    )
{
}

void Oscillator::reset_state() {
  for (auto &bundle : bundles) {
    bundle.state = 0;
  }
}

SigT Oscillator::poly_blep(SigT t, SigT dt) {
  dt = std::abs(dt);
  if (t < dt) {
    t /= dt;
    return -t*t +2*t -1;
  } else if (t > 1-dt) {
    t = (t-1)/dt;
    return t*t +2*t +1;
  }
  return 0.;
}

Universe::Descriptor Oscillator::infer_polyphony_operation(std::vector<Universe::Pointer> inputs) {
  Universe::Descriptor result;
  // Prioritize frequency input
  if (inputs[InputSockets::frequency]->is_polyphonic()) {
    result.set_all(inputs[InputSockets::frequency]);
  } else {
    for (auto uni : inputs) {
      if (uni->is_polyphonic()) {
        result.set_all(uni);
        break;
      }
    }
  }
  return result;
}

void Oscillator::apply_bundle_universe_changes(const Universe &universe) {
  universe.apply_delta(bundles);
}

void Oscillator::process(NodeInputWindow &input) {
  size_t n = input.get_channel_amount();
  AudioData::PolyWriter output(output_window[0], n);
  
  const int f_id = get_property_value(Properties::oscillation_func);
  const int anti_alias = get_property_value(Properties::anti_alias);
  
  for (size_t i = 0; i < n; ++i) {
    const Chunk
      &frequency = input[InputSockets::frequency][i],
      &amplitude = input[InputSockets::amplitude][i],
      &offset    = input[InputSockets::offset][i],
      &param     = input[InputSockets::param][i];
    Chunk &channel = output[i];
    SigT state = bundles[i].state;
    SigT last_val = bundles[i].last_val;
    for (size_t j = 0; j < N; ++j) {
      SigT step = frequency[j]/RATE;
      state = std::fmod(state + step, 1);
      if (state < 0) state += 1;
      switch (f_id) {
        case Modes::sine:
          channel[j] = std::sin(state*2*M_PI);
          break;
        case Modes::saw:
          channel[j] = state*2-1;
          break;
        case Modes::square:
          channel[j] = state > 1-param[j] ? 1. : -1.;
          break;
        case Modes::triangle:
          if (anti_alias) {
            // Will be integrated
            channel[j] = state > 0.5 ? 1. : -1.;
          } else {
            channel[j] = std::fabs(4*state-2)-1;
          }
      }
      if (anti_alias) {
        switch (f_id) {
          case Modes::saw:
            channel[j] -= poly_blep(state, step);
            break;
          case Modes::square:
            channel[j] -= poly_blep(state, step);
            channel[j] += poly_blep(std::fmod(state+param[j], 1), step);
            break;
          case Modes::triangle:
            channel[j] -= poly_blep(state, step);
            channel[j] += poly_blep(std::fmod(state+0.5, 1), step);
            
            // Leaky integrator
            channel[j] = std::abs(step)*channel[j]*4 + (1-std::abs(step))*last_val;
            last_val = channel[j];
            break;
        }
      }
      channel[j] = channel[j] * amplitude[j] + offset[j];
    }
    bundles[i] = {state, last_val};
  }
}


}
