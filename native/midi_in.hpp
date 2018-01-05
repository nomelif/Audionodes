
#ifndef MIDI_IN_HPP
#define MIDI_IN_HPP

#include "common.hpp"
#include "node.hpp"
#include "fluidsynth.h"
#include <iostream>
#include "midi_data.hpp"
#include "circular_buffer.hpp"

class MidiIn : public Node {
  // typedef std::chrono::steady_clock Clock;
  // typedef std::chrono::duration<size_t, std::ratio<1, rate>> SampleDuration;
  fluid_midi_driver_t* driver;
  static int handle_midi_event(void* data, fluid_midi_event_t* event);
  CircularBuffer<MidiData::Event, 1024> event_buffer;
  public:
  MidiIn();
  ~MidiIn();
  NodeOutputWindow process(NodeInputWindow&);
};


#endif
