#include "pitch_bend.hpp"
#include <iostream>

PitchBend::PitchBend() :
    Node({SocketType::midi}, {SocketType::audio}, {})
{
  bend_state = 0;
}

Universe::Descriptor PitchBend::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  return Universe::Descriptor();
}

NodeOutputWindow PitchBend::process(NodeInputWindow &input) {

  Chunk bend;
  const MidiData &midi = input[InputSockets::midi_in].get<MidiData>();
  SigT new_state = bend_state;
  for (const MidiData::Event event : midi.events) {
    if (event.get_type() == MidiData::EType::pitch_bend) {
      new_state = SigT(event.get_bend()-8192)/8192;
    }
  }

  //std::cout << bend_state << std::endl;
  for (size_t j = 0; j < N; ++j) {
    SigT result = (bend_state*(N-j) + new_state*j)/N;
    bend[j] = result;
  }
  bend_state = new_state;
  return NodeOutputWindow({new AudioData(bend)});
}
