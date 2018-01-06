#ifndef MIDI_DATA_HPP
#define MIDI_DATA_HPP

#include "common.hpp"
#include "data.hpp"

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
    Type get_type();
    int get_channel();
    int get_note();
    int get_velocity();
    int get_bend();
    int get_aftertouch();
    bool is_panic();
    bool is_sustain();
    bool is_sustain_enable();
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


#endif
