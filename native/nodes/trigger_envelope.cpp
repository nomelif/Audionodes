#include "nodes/trigger_envelope.hpp"

namespace audionodes {

static NodeTypeRegistration<TriggerEnvelope> registration("TriggerEnvelopeNode");

TriggerEnvelope::TriggerEnvelope() :
    Node({
      SocketType::trigger,
      SocketType::audio, SocketType::audio, SocketType::audio,
      SocketType::audio,
      SocketType::audio, SocketType::audio, SocketType::audio
    },
    {SocketType::audio},
    {})
{}

Universe::Descriptor TriggerEnvelope::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  Universe::Pointer mono(new Universe());
  return {mono, mono, mono};
}

void TriggerEnvelope::process(NodeInputWindow &input) {
  auto &trigger = input[InputSockets::trigger].get<TriggerData>();
  auto &delay_time = input[InputSockets::delay_time][0];
  auto &attack_time = input[InputSockets::attack_time][0];
  auto &hold_time = input[InputSockets::hold_time][0];
  auto &hold_level = input[InputSockets::hold_level][0];
  auto &attack_slope = input[InputSockets::attack_slope][0];
  auto &decay_slope = input[InputSockets::decay_slope][0];
  auto &release_slope = input[InputSockets::release_slope][0];
  Chunk &output = output_window[OutputSockets::envelope].mono;
  auto it = trigger.iterate();
  for (size_t i = 0; i < N; ++i) {
    if (it.count(i)) {
      if (delay_time[i] < 1./RATE) {
        current_phase = Phase::attack;
      } else {
        current_phase = Phase::waiting;
      }
      time_elapsed = 0;
    }
    SigT target = 0, slope = 0;
    switch (current_phase) {
      case Phase::released:
        target = 0;
        slope = release_slope[i];
      break;
      case Phase::waiting:
        target = 0;
        slope = release_slope[i];
        if (time_elapsed > long(delay_time[i]*RATE)) {
          current_phase = Phase::attack;
          time_elapsed = 0;
        }
      break;
      case Phase::attack:
        target = 1;
        slope = attack_slope[i];
        if (time_elapsed > long(attack_time[i]*RATE)) {
          current_phase = Phase::hold;
          time_elapsed = 0;
        }
      break;
      case Phase::hold:
        target = hold_level[i];
        slope = decay_slope[i];
        if (time_elapsed > long(hold_time[i]*RATE)) {
          current_phase = Phase::released;
          time_elapsed = 0;
        }
      break;
    }
    slope = std::exp(slope - 4);
    current_state = current_state*(1.-slope) + target*slope;
    if (current_state > 1) current_state = 1;
    if (current_state < 0) current_state = 0;
    output[i] = current_state;
    time_elapsed++;
  }
}

}
