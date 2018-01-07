#include "midi_data.hpp"

MidiData::Event::Type MidiData::Event::get_type() const {
  switch (raw_type) {
    case 0x8:
      return Type::note_off;
    case 0x9:
      return Type::note_on;
    case 0xA:
      return Type::polyphonic_aftertouch;
    case 0xB:
      return Type::control;
    case 0xC:
      return Type::program;
    case 0xD:
      return Type::channel_aftertouch;
    case 0xE:
      return Type::pitch_bend;
    default:
      return Type::undef;
  }
}

unsigned char MidiData::Event::get_type_value(Type type) {
  switch (type) {
    case Type::note_off:
      return 0x8;
    case Type::note_on:
      return 0x9;
    case Type::polyphonic_aftertouch:
      return 0xA;
    case Type::control:
      return 0xB;
    case Type::program:
      return 0xC;
    case Type::channel_aftertouch:
      return 0xD;
    case Type::pitch_bend:
      return 0xE;
    default:
      return 0;
  }
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
  return param2;
}

int MidiData::Event::get_aftertouch() const {
  if (get_type() == Type::polyphonic_aftertouch) {
    return param2;
  } else {
    return param1;
  }
}

bool MidiData::Event::is_panic() const {
  return (get_type() == Type::control) && (param1 == 0x7b);
}

bool MidiData::Event::is_sustain() const {
  return (get_type() == Type::control) && (param1 == 0x40);
}

bool MidiData::Event::is_sustain_enable() const {
  return is_sustain() && (param2 > 0x40);
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

MidiData MidiData::dummy = MidiData();
