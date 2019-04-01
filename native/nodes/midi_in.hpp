
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
  std::map<std::string, const char*> internal_setting_names = {
    {"driver", "midi.driver"},
    {"portname", "midi.portname"},
    {"alsa_raw_device", "midi.alsa.device"},
    {"jack_server", "midi.jack.server"},
    {"oss_device", "midi.oss.device"},
    {"win_device", "midi.winmidi.device"}
  };
  // Fluid doesn't return these as options
  std::map<std::string, std::string> implicit_default_value = {
    {"win_device", "default"}
  };
 
  fluid_midi_driver_t *driver = nullptr;
  fluid_settings_t *settings = nullptr;
  static int handle_midi_event(void* data, fluid_midi_event_t* event);
  CircularBuffer<MidiData::Event, 1024> event_buffer;
  std::atomic<bool> overflow_flag;
  
  bool apply_configuration();
  void reset_configuration();
  public:
  MidiIn();
  MidiIn(MidiIn&);
  ~MidiIn();
  ConfigurationDescriptorList get_configuration_options() override;
  int set_configuration_option(std::string, std::string) override;
  void process(NodeInputWindow&) override;
};

}

#endif
