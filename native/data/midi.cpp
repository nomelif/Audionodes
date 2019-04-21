#include "data/midi.hpp"

namespace audionodes {

MidiData::Event::Type MidiData::Event::get_type() const {
  if (raw_type >= 0x8 && raw_type <= 0xE) {
    return static_cast<Type>(raw_type);
  } else {
    return Type::undef;
  }
}

unsigned char MidiData::Event::get_type_value(Type type) {
  return static_cast<unsigned char>(type);
}

int MidiData::Event::get_channel() const {
  return raw_channel;
}

int MidiData::Event::get_note() const {
  return param1;
}

int MidiData::Event::get_velocity() const {
  return param2;
}

int MidiData::Event::get_bend() const {
  return (int)param2 << 7 | param1;
}

int MidiData::Event::get_aftertouch() const {
  if (get_type() == Type::polyphonic_aftertouch) {
    return param2;
  } else {
    return param1;
  }
}

bool MidiData::Event::is_panic() const {
  return get_type() == Type::control && param1 == 0x7b;
}

bool MidiData::Event::is_sustain() const {
  return get_type() == Type::control && param1 == 0x40;
}

bool MidiData::Event::is_sostenuto() const {
  return get_type() == Type::control && param1 == 0x42;
}

bool MidiData::Event::is_pedal_down() const {
  return param2 >= 0x40;
}

MidiData::Event::Event(
  unsigned char type, unsigned char channel, unsigned char param1, unsigned char param2) :
    raw_type(type),
    raw_channel(channel),
    param1(param1),
    param2(param2)
{
}

MidiData::Event::Event(
  Type type, unsigned char channel, unsigned char param1, unsigned char param2) :
    Event(get_type_value(type), channel, param1, param2)
{}
  

MidiData::Event::Event() {}

MidiData::MidiData(EventSeries events) :
  events(events)
{}

MidiData::MidiData() {}

void MidiData::clear() {
  events.clear();
}

MidiData MidiData::dummy = MidiData();

}
