#ifndef MIDI_HELPER_HPP
#define MIDI_HELPER_HPP

#include "common.hpp"

enum EvtType {
  NOTE_OFF,
  NOTE_ON,
  POLYPHONIC_AFTERTOUCH,
  CONTROL,
  PROGRAM,
  CHANNEL_AFTERTOUCH,
  PITCH_BEND,
  UNDEF
};

EvtType getType(MidiMSG msg);
int getChannel(MidiMSG msg);
int getNote(MidiMSG msg);
int getVelocity(MidiMSG msg);
int getBend(MidiMSG msg);
int getAftertouch(MidiMSG msg);
bool isPanic(MidiMSG msg);
bool isSustain(MidiMSG msg);
bool isSustainEnable(MidiMSG msg);

#endif
