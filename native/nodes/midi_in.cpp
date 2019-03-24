#include "nodes/midi_in.hpp"

namespace audionodes {

static NodeTypeRegistration<MidiIn> registration("MidiInNode");

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
  settings = new_fluid_settings();
  if (fluid_settings_get_type(settings, "midi.portname") == FLUID_STR_TYPE) {
    fluid_settings_setstr(settings, "midi.portname", "Audionodes");
  }
  driver = new_fluid_midi_driver(settings, handle_midi_event, this);
  if (!driver) {
    std::cerr << "Audionodes Native: Unable to create MIDI device via Fluidsynth" << std::endl;
  }
}

MidiIn::~MidiIn()
{
  if (settings) delete_fluid_settings(settings);
  if (driver) delete_fluid_midi_driver(driver);
}

std::string MidiIn::get_current_driver() {
  std::vector<char> buf(256);
  fluid_settings_copystr(settings, "midi.driver", buf.data(), buf.size());
  return std::string(buf.data());
}

std::string MidiIn::get_device_setting_name() {
  std::string setting_name = "midi.";
  setting_name += get_current_driver();
  setting_name += ".device";
  return setting_name;
}

Node::ConfigurationDescriptor MidiIn::get_configuration_options(int slot) {
  std::vector<char> buf(256);
  std::vector<std::string> list;
  fluid_settings_t *tmp_settings = new_fluid_settings();
  
  std::string setting_name;
  switch (slot) {
    case conf_driver:
      setting_name = "midi.driver";
      break;
    case conf_device:
      setting_name = get_device_setting_name();
      list.push_back("default");
      break;
    default: // Invalid
      return {buf.data(), list};
      break;
  }
  
  if (fluid_settings_get_type(tmp_settings, setting_name.c_str()) == FLUID_STR_TYPE) {
    fluid_settings_foreach_option(tmp_settings, setting_name.c_str(), &list,
    [](void *lp, char *name, char *option) {
      static_cast<decltype(list)*>(lp)->emplace_back(option);
    });
    fluid_settings_copystr(settings, setting_name.c_str(), buf.data(), buf.size());
  }
  
  delete_fluid_settings(tmp_settings);
  return {buf.data(), list};
}

int MidiIn::set_configuration_option(int slot, std::string value) {
  std::string setting_name;
  switch (slot) {
    case conf_driver:
      setting_name = "midi.driver";
      break;
    case conf_device:
      setting_name = get_device_setting_name();
      break;
    case conf_commit:
      return apply_settings();
      break;
  }
  if (fluid_settings_get_type(settings, setting_name.c_str()) == FLUID_STR_TYPE) {
    fluid_settings_setstr(settings, setting_name.c_str(), value.c_str());
    return true;
  }
  return false;
}

bool MidiIn::apply_settings() {
  if (driver) delete_fluid_midi_driver(driver);
  driver = new_fluid_midi_driver(settings, handle_midi_event, this);
  return driver != nullptr;
}

void MidiIn::process(NodeInputWindow &input) {
  MidiData::EventSeries &events = output_window.get<MidiData>(0).events;
  events.clear();
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
}

}
