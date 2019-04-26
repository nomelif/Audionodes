#include "nodes/toggle.hpp"

namespace audionodes {

static NodeTypeRegistration<Toggle> registration("ToggleNode");

Toggle::Toggle() :
    Node({SocketType::trigger, SocketType::audio, SocketType::audio}, {SocketType::audio}, {})
{}

void Toggle::process(NodeInputWindow &input) {
  auto &s_a = input[InputSockets::signal_a];
  auto &s_b = input[InputSockets::signal_b];
  auto &triggers = input[InputSockets::trigger].get<TriggerData>();
  if (triggers.reset) a_on = true;
  size_t n = input.get_channel_amount();
  AudioData::PolyWriter output(output_window[0], n);
  for(size_t i = 0; i < n; i++){
    bool state = a_on;
    size_t k = 0;
    auto it = triggers.iterate();
    for(size_t j = 0; j < N; j++){
      state ^= it.count(j) % 2;
      if(state)
        output[i][j] = s_a[i][j];
      else
        output[i][j] = s_b[i][j];
    }
  }
  a_on ^= triggers.events.size() % 2;
}

}
