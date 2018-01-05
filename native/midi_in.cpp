#include "midi_in.hpp"

int MidiIn::handle_midi_event(void* _node, fluid_midi_event_t* event){
  using namespace std::chrono;
  MidiIn *node = (MidiIn*)_node;
  if (!node->mark_connected) return 0;
  MidiData::Event our_event(
    fluid_midi_event_get_type(event),
    fluid_midi_event_get_channel(event),
    // Corresponds to param1
    fluid_midi_event_get_key(event),
    // Corresponds to param2
    fluid_midi_event_get_velocity(event)
  );
  // TODO: buffer full
  node->event_buffer.push(our_event);
  return 0;
}

MidiIn::MidiIn() :
  Node(0, 1, 0),
  event_buffer(false)
{
  fluid_settings_t* settings = new_fluid_settings();
  fluid_settings_setstr(settings, "midi.portname", "Audionodes");
  driver = new_fluid_midi_driver(settings, handle_midi_event, this);
}

MidiIn::~MidiIn()
{
  delete_fluid_midi_driver(driver);
}

NodeOutputWindow MidiIn::process(NodeInputWindow &input) {
  MidiData::EventSeries events;
  while (!event_buffer.empty()) {
    events.push_back(event_buffer.pop());
  }
  return NodeOutputWindow({new MidiData(events)});
}
