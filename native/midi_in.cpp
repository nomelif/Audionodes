#include "midi_in.hpp"

using namespace std;
using namespace std::chrono;

int MidiIn::handle_midi_event(void* data, fluid_midi_event_t* event){

  // Ruubi on hyvä

  return 0;
}

MidiIn::MidiIn() :
    Node(0, 1, 0)
{
  fluid_settings_t* settings = new_fluid_settings();
  driver = new_fluid_midi_driver(settings, handle_midi_event, this);
}

MidiIn::~MidiIn()
{
  delete_fluid_midi_driver(driver);
}



NodeOutputWindow MidiIn::process(NodeInputWindow &input) {
  MidiData::EventSeries events;
  NodeOutputWindow result = NodeOutputWindow({new MidiData(events)});
  return result;
}
