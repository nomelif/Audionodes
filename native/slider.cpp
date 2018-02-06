#include "slider.hpp"
#include <iostream>

Slider::Slider() :
    Node({SocketType::midi}, {SocketType::audio}, {PropertyType::integer, PropertyType::select})
{
  value_state = 0;
}

Universe::Descriptor Slider::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  return Universe::Descriptor();
}

NodeOutputWindow Slider::process(NodeInputWindow &input) {
  int channel = get_property_value(Properties::channel);
  int interfaceType = get_property_value(Properties::interfaceType);
  static const int controlMask[] = {7, 10};
  Chunk value;
  const MidiData &midi = input[InputSockets::midi_in].get<MidiData>();
  SigT new_state = value_state;
  for (const MidiData::Event event : midi.events) {
    if (event.get_type() == MidiData::EType::control && channel == event.get_channel()+1 && event.get_note() == controlMask[interfaceType]) {
      new_state = SigT(event.get_bend())/16384;
    }
  }

  for (size_t j = 0; j < N; ++j) {
    SigT result = (value_state*(N-j) + new_state*j)/N;
    value[j] = result;
  }
  value_state = new_state;
  return NodeOutputWindow({new AudioData(value)});
}
