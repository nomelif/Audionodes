#include "nodes/midi_in.hpp"
#include <iostream>
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
  reset_configuration();
  apply_configuration();
  if (!driver) {
    std::cerr << "Audionodes Native: Unable to create MIDI device via Fluidsynth" << std::endl;
  }
}

MidiIn::MidiIn(MidiIn &from) :
    Node(from),
    event_buffer(false),
    overflow_flag(false)
{
  settings = new_fluid_settings();
  std::vector<char> buf(256);
  for (auto &sname : internal_setting_names) {
    if (fluid_settings_get_type(settings, sname.second) == FLUID_STR_TYPE) {
      fluid_settings_copystr(from.settings, sname.second, buf.data(), buf.size());
      fluid_settings_setstr(settings, sname.second, buf.data());
    }
  }
  std::cout << driver << std::endl;
  apply_configuration();
}

MidiIn::~MidiIn()
{
  if (settings) delete_fluid_settings(settings);
  if (driver) delete_fluid_midi_driver(driver);
}


Node::ConfigurationDescriptorList MidiIn::get_configuration_options() {
  std::vector<char> buf(256);
  ConfigurationDescriptorList list;
  fluid_settings_t *tmp_settings = new_fluid_settings();
  
  for (auto &sname : internal_setting_names) {
    if (fluid_settings_get_type(tmp_settings, sname.second) == FLUID_STR_TYPE) {
      ConfigurationDescriptor desc;
      desc.name = sname.first;
      fluid_settings_foreach_option(tmp_settings, sname.second, &desc.available_values,
      [](void *lp, char *name, char *option) {
        static_cast<decltype(desc.available_values)*>(lp)->emplace_back(option);
      });
      fluid_settings_copystr(settings, sname.second, buf.data(), buf.size());
      desc.current_value = std::string(buf.data());
      list.push_back(desc);
    }
  }
  
  delete_fluid_settings(tmp_settings);
  return list;
}

int MidiIn::set_configuration_option(std::string name, std::string value) {
  if (name == "reset_configuration") {
    reset_configuration();
    return 1;
  } else if (name == "apply_configuration") {
    return apply_configuration();
  } else if (internal_setting_names.count(name)) {
    if (name == "portname" && value == "") value = "Audionodes";
    const char *setting_name = internal_setting_names[name];
    if (fluid_settings_get_type(settings, setting_name) == FLUID_STR_TYPE) {
      fluid_settings_setstr(settings, setting_name, value.c_str());
      return 1;
    } else return 2;
  } else return 0;
}

void MidiIn::reset_configuration() {
  if (settings) delete_fluid_settings(settings);
  settings = new_fluid_settings();
  if (fluid_settings_get_type(settings, "midi.portname") == FLUID_STR_TYPE) {
    fluid_settings_setstr(settings, "midi.portname", "Audionodes");
  }
}

bool MidiIn::apply_configuration() {
  if (driver) delete_fluid_midi_driver(driver);
  driver = new_fluid_midi_driver(settings, handle_midi_event, this);
  return driver != nullptr;
}

void MidiIn::process(NodeInputWindow &input) {
  MidiData::EventSeries &events = output_window.get_clear<MidiData>(0).events;
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
