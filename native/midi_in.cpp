#include "midi_in.hpp"

int MidiIn::handle_midi_event(void* _node, fluid_midi_event_t* event){
  MidiIn *node = (MidiIn*)_node;
  if (!node->mark_connected) return 0;
  MidiData::Event our_event(
    fluid_midi_event_get_type(event) >> 4,
    fluid_midi_event_get_channel(event),
    // Corresponds to param1
    fluid_midi_event_get_key(event),
    // Corresponds to param2
    fluid_midi_event_get_velocity(event)
  );
  if (fluid_midi_event_get_type(event) >> 4 == 0xE) {
    // Pitch bend special case: fluid gives the bend data in param1 pre-packaged
    // -> convert back to standard midi representation
    int bend = fluid_midi_event_get_key(event);
    our_event.param1 = bend & 0x7F;
    our_event.param2 = bend >> 7;
  }
  if (our_event.get_type() == MidiData::EType::note_on && our_event.get_velocity() == 0) {
    our_event.raw_type = MidiData::Event::get_type_value(MidiData::EType::note_off);
  }
  if (!node->overflow_flag) {
    if (node->event_buffer.full()) {
      // Signal buffer overflow
      node->overflow_flag = true;
      std::clog << "Audionodes native: Buffer overflow at MIDI input!" << std::endl;
    } else {
      node->event_buffer.push(our_event);
    }
  } else {
    // Node hasn't responded to overflow yet, can't do anything
  }
  return 0;
}

MidiIn::MidiIn() :
  Node({}, {SocketType::midi}, {}),
  event_buffer(false),
  overflow_flag(false)
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
  if (!overflow_flag) {
    while (!event_buffer.empty()) {
      events.push_back(event_buffer.pop());
    }
  } else {
    // Buffer overflow occured
    event_buffer.clear();
    // Emit panic signal on all channels
    for (unsigned char chan = 0; chan < 16; ++chan) {
      // CC 120, CC 121, CC 123
      events.emplace_back(MidiData::EType::control, chan, 120, 0);
      events.emplace_back(MidiData::EType::control, chan, 121, 0);
      events.emplace_back(MidiData::EType::control, chan, 123, 0);
    }
    overflow_flag = false;
  }
  return NodeOutputWindow({new MidiData(events)});
}
