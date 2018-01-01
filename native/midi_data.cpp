#include "midi_data.hpp"

MidiData::Event::Type MidiData::Event::get_type() {
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

int MidiData::Event::get_channel() {
  return raw_channel;
}

int MidiData::Event::get_note() {
  return param1;
}

int MidiData::Event::get_velocity() {
  return param2;
}

int MidiData::Event::get_bend() {
  return param2;
}

int MidiData::Event::get_aftertouch() {
  if (get_type() == Type::polyphonic_aftertouch) {
    return param2;
  } else {
    return param1;
  }
}

bool MidiData::Event::is_panic() {
  return (get_type() == Type::control) && (param1 == 0x7b);
}

bool MidiData::Event::is_sustain() {
  return (get_type() == Type::control) && (param1 == 0x40);
}

bool MidiData::Event::is_sustain_enable() {
  return is_sustain() && (param2 > 0x40);
}

MidiData::Event::Event(
  size_t time, unsigned char type, unsigned char channel, unsigned int param1, unsigned int param2) :
  time(time),
  raw_type(type),
  raw_channel(channel),
  param1(param1),
  param2(param2)
{}

MidiData::MidiData(EventSeries events) :
  events(events)
{}

MidiData::MidiData() {}

MidiData MidiData::dummy = MidiData();
