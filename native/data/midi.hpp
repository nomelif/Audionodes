#ifndef MIDI_DATA_HPP
#define MIDI_DATA_HPP

#include "common.hpp"
#include "data/data.hpp"

namespace audionodes {

struct MidiData : public Data {
  struct Event {
    enum class Type {
      note_off,
      note_on,
      polyphonic_aftertouch,
      control,
      program,
      channel_aftertouch,
      pitch_bend,
      undef
    };
    unsigned char raw_type, raw_channel, param1, param2;
    
    static unsigned char get_type_value(Type);
    Type get_type() const;
    int get_channel() const;
    int get_note() const;
    int get_velocity() const;
    int get_bend() const;
    int get_aftertouch() const;
    bool is_panic() const;
    bool is_sustain() const;
    bool is_sostenuto() const;
    bool is_pedal_down() const;
    Event(unsigned char, unsigned char, unsigned char, unsigned char);
    Event(Type, unsigned char, unsigned char, unsigned char);
    Event();
  };
  
  typedef std::vector<Event> EventSeries;
  typedef Event::Type EType; // helper
  EventSeries events;
  
  MidiData(EventSeries);
  MidiData();
  
  static MidiData dummy;
};

}

#endif
