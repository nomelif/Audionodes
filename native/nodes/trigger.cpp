#include "nodes/trigger.hpp"

#include <iostream>

Trigger::Trigger() :
    Node({SocketType::midi}, {SocketType::trigger}, {PropertyType::integer})
{}

Universe::Descriptor Trigger::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  return Universe::Descriptor();
}

void Trigger::process(NodeInputWindow &input) {
  const MidiData &midi = input[InputSockets::midi_in].get<MidiData>();
  int channel = get_property_value(Properties::channel);
  TriggerData::EventSeries &triggers = output_window.get<TriggerData>(0).events;
  triggers.clear();
  for(const MidiData::Event event : midi.events){
    if(event.get_type() == MidiData::EType::control && event.get_note() == channel){
      triggers.push_back(0);
    }
  }
}
