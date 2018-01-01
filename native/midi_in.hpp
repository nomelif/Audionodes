
#ifndef MIDI_IN_HPP
#define MIDI_IN_HPP

#include "common.hpp"
#include "node.hpp"
#include "fluidsynth.h"
#include <iostream>
#include <chrono>
#include "midi_data.hpp"

class MidiIn : public Node {
  typedef std::chrono::steady_clock Clock;
  fluid_midi_driver_t* driver;
  static int handle_midi_event(void* data, fluid_midi_event_t* event);
  typedef std::vector<std::pair<Clock::time_point, MidiData::Event>> EventBuffer;
  EventBuffer event_buffer;
  std::mutex event_buffer_mutex;
  Clock::time_point last_process;
  bool accept_events();
  public:
  MidiIn();
  ~MidiIn();
  NodeOutputWindow process(NodeInputWindow&);
};


#endif
