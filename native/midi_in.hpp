
#ifndef MIDI_IN_HPP
#define MIDI_IN_HPP

#include "common.hpp"
#include "node.hpp"
#include "fluidsynth.h"
#include <iostream>
#include <chrono>
#include "midi_data.hpp"
#include <vector>


class MidiIn : public Node {
  enum InputSockets {
    frequency, amplitude, offset, param
  };
  fluid_midi_driver_t* driver;
  public:
  MidiIn();
  ~MidiIn();
  NodeOutputWindow process(NodeInputWindow&);
  static int handle_midi_event(void* data, fluid_midi_event_t* event);

};



#endif
