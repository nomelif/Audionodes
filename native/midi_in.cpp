#include "midi_in.hpp"


#include <iostream>
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
  std::lock_guard<std::mutex> lock(node->event_buffer_mutex);
  Clock::time_point time = Clock::now();
  our_event.time = (
    duration_cast<SampleDuration>(time - node->last_process)
    + node->timing_offset
  ).count();
  bool to_next = false;
  if (our_event.time >= N) {
    our_event.time -= N;
    to_next = true;
  }
  our_event.time = std::min(std::max(our_event.time, size_t(0)), N-1);
  if (!to_next) {
    node->event_buffer.push_back(our_event);
  } else {
    node->event_buffer_to_next.push_back(our_event);
  }
  return 0;
}

MidiIn::MidiIn() :
  Node(0, 1, 0)
{
  fluid_settings_t* settings = new_fluid_settings();
  fluid_settings_setstr(settings, "midi.portname", "Audionodes");
  driver = new_fluid_midi_driver(settings, handle_midi_event, this);
  last_process = Clock::time_point();
}

MidiIn::~MidiIn()
{
  delete_fluid_midi_driver(driver);
}

NodeOutputWindow MidiIn::process(NodeInputWindow &input) {
  MidiData::EventSeries events;
  { std::lock_guard<std::mutex> lock(event_buffer_mutex);
    events = std::move(event_buffer);
    event_buffer = std::move(event_buffer_to_next);
    event_buffer_to_next = MidiData::EventSeries();
    Clock::time_point this_process = Clock::now();
    timing_offset = std::chrono::duration_cast<SampleDuration>(this_process-last_process);
    if (timing_offset < SampleDuration(N)) timing_offset = SampleDuration(0);
    else timing_offset -= SampleDuration(N);
    last_process = this_process;
  }
  for (auto &p : events) {
    std::cout << p.time << std::endl;
  }
  return NodeOutputWindow({new MidiData(events)});
}
