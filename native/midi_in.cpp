#include "midi_in.hpp"


int MidiIn::handle_midi_event(void* _node, fluid_midi_event_t* event){
  MidiIn *node = (MidiIn*)_node;
  if (!node->accept_events()) return 0;
  MidiData::Event our_event(
    fluid_midi_event_get_type(event),
    fluid_midi_event_get_channel(event),
    // Corresponds to param1
    fluid_midi_event_get_key(event),
    // Corresponds to param2
    fluid_midi_event_get_velocity(event)
  );
  Clock::time_point time = Clock::now();
  std::lock_guard<std::mutex> lock(node->event_buffer_mutex);
  node->event_buffer.push_back({time, our_event});
  return 0;
}

bool MidiIn::accept_events() {
  return (Clock::now() - last_process).count() < 2*double(N)/rate;
}

MidiIn::MidiIn() :
  Node(0, 1, 0)
{
  fluid_settings_t* settings = new_fluid_settings();
  driver = new_fluid_midi_driver(settings, handle_midi_event, this);
  last_process = Clock::time_point();
}

MidiIn::~MidiIn()
{
  delete_fluid_midi_driver(driver);
}



NodeOutputWindow MidiIn::process(NodeInputWindow &input) {
  EventBuffer buffer_copy;
  {
    std::lock_guard<std::mutex> lock(event_buffer_mutex);
    buffer_copy = std::move(event_buffer);
    event_buffer = EventBuffer();
  }
  MidiData::EventSeries events;
  events.reserve(buffer_copy.size());
  Clock::time_point this_process = Clock::now();
  for (auto p : buffer_copy) {
    p.second.time = std::round((p.first - last_process).count()*rate);
    p.second.time = std::min(std::max(p.second.time, size_t(0)), N-1);
    events.push_back(p.second);
  }
  last_process = this_process;
  return NodeOutputWindow({new MidiData(events)});
}
