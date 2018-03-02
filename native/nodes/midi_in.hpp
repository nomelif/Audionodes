
#ifndef MIDI_IN_HPP
#define MIDI_IN_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include "util/circular_buffer.hpp"

#include "fluidsynth.h"
#include <iostream>
#include <atomic>

class MidiIn : public Node {
  fluid_midi_driver_t* driver;
  static int handle_midi_event(void* data, fluid_midi_event_t* event);
  CircularBuffer<MidiData::Event, 1024> event_buffer;
  std::atomic<bool> overflow_flag;
  public:
  MidiIn();
  ~MidiIn();
  void process(NodeInputWindow&);
};


#endif
