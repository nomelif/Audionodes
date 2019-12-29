#include "nodes/midi_control.hpp"

namespace audionodes {

static NodeTypeRegistration<MIDIControl> registration("MIDIControlNode");

MIDIControl::MIDIControl() :
    Node({SocketType::midi}, {SocketType::audio}, {PropertyType::integer, PropertyType::integer})
{
  value_state = 0;
}

Universe::Descriptor MIDIControl::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  return Universe::Descriptor();
}

void MIDIControl::process(NodeInputWindow &input) {
  int channel = get_property_value(Properties::channel);
  int cc_no = get_property_value(Properties::cc_no);
  Chunk &value = output_window[0].mono;
  const MidiData &midi = input[InputSockets::midi_in].get<MidiData>();
  SigT new_state = value_state;
  for (const MidiData::Event event : midi.events) {
    if (event.get_type() == MidiData::EType::control
        && (!channel || channel == event.get_channel()+1)
        && cc_no == event.get_note()) {
      new_state = SigT(event.get_velocity())/127;
    }
  }

  if (value_state == new_state) {
    value.fill(value_state);
  } else {
    for (size_t j = 0; j < N; ++j) {
      SigT result = (value_state*(N-j) + new_state*j)/N;
      value[j] = result;
    }
    value_state = new_state;
  }
}

}
