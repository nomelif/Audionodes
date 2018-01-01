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
    size_t time;
    bool operator<(const Event) const;
    unsigned char raw_type, raw_channel;
    unsigned int param1, param2;
    
    Type get_type();
    int get_channel();
    int get_note();
    int get_velocity();
    int get_bend();
    int get_aftertouch();
    bool is_panic();
    bool is_sustain();
    bool is_sustain_enable();
    Event(unsigned char, unsigned char, unsigned int, unsigned int, size_t time = 0);
  };
  
  typedef std::vector<Event> EventSeries;
  EventSeries events;
  
  MidiData(EventSeries);
  MidiData();
  
  static MidiData dummy;
};


#endif
