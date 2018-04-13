#include "nodes/midi_trigger.hpp"

MidiTrigger::MidiTrigger() :
    Node({SocketType::midi}, {SocketType::trigger}, {PropertyType::integer, PropertyType::select})
{}

Universe::Descriptor MidiTrigger::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  return Universe::Descriptor();
}

void MidiTrigger::process(NodeInputWindow &input) {
  const MidiData &midi = input[InputSockets::midi_in].get<MidiData>();
  int channel = get_property_value(Properties::channel);
  TriggerData::EventSeries &triggers = output_window.get<TriggerData>(0).events;
  triggers.clear();
  for(const MidiData::Event event : midi.events){
    if(get_property_value(Properties::interfaceType) == 0){
      if(event.get_type() == MidiData::EType::control && event.get_note() == channel){
        triggers.push_back(0);
      }
    }else{
      if(event.get_type() == MidiData::EType::note_on && event.get_note() == channel){
        triggers.push_back(0);
      }
    }
  }
}
