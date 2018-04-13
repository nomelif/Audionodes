#include "nodes/toggle.hpp"

#include <iostream>

Toggle::Toggle() :
    Node({SocketType::trigger, SocketType::audio, SocketType::audio}, {SocketType::audio}, {})
{}

/*Universe::Descriptor Toggle::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  return Universe::Descriptor();
}*/

void Toggle::process(NodeInputWindow &input) {
  auto &s_a = input[InputSockets::signal_a];
  auto &s_b = input[InputSockets::signal_b];
  auto &triggers = input[InputSockets::trigger].get<TriggerData>();
  //output[OutputSockets::output].resize(s_a.get_channel_amount());
  AudioData::PolyWriter output(output_window[0]);
  output.resize(input.get_channel_amount());
  for(size_t i = 0; i < input.get_channel_amount(); i++){
    bool state = a_on;
    int k = 0;
    for(size_t j = 0; j < N; j++){
      if(k < triggers.events.size() && triggers.events[k] <= j){
        state = !state;
        k++;
      }
      if(state)
        output[i][j] = input[InputSockets::signal_a][i][j];
      else
        output[i][j] = input[InputSockets::signal_b][i][j];
    }
  }
  a_on ^= triggers.events.size() % 2;
}
