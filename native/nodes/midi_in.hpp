
#ifndef MIDI_IN_HPP
#define MIDI_IN_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include "util/circular_buffer.hpp"

#include "fluidsynth.h"
#include <iostream>
#include <atomic>

namespace audionodes {

class MidiIn : public Node {
  enum ConfSlots {
    conf_driver, conf_device, 
    conf_commit // no value, just command to commit configuration and reopen device
  };
  
  fluid_midi_driver_t *driver;
  fluid_settings_t *settings;
  static int handle_midi_event(void* data, fluid_midi_event_t* event);
  CircularBuffer<MidiData::Event, 1024> event_buffer;
  std::atomic<bool> overflow_flag;
  
  std::string get_current_driver();
  std::string get_device_setting_name();
  bool apply_settings();
  public:
  MidiIn();
  ~MidiIn();
  ConfigurationDescriptor get_configuration_options(int) override;
  int set_configuration_option(int, std::string) override;
  void process(NodeInputWindow&) override;
};

}

#endif
