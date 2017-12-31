#include "midi_helper.hpp"

EvtType getType(MidiMSG msg){
  switch (msg >> 20) {
    case 0x8:
      return EvtType::NOTE_OFF;
    case 0x9:
      return EvtType::NOTE_ON;
    case 0xA:
      return EvtType::POLYPHONIC_AFTERTOUCH;
    case 0xB:
      return EvtType::CONTROL;
    case 0xC:
      return EvtType::PROGRAM;
    case 0xD:
      return EvtType::CHANNEL_AFTERTOUCH;
    case 0xE:
      return EvtType::PITCH_BEND;
    default:
      return EvtType::UNDEF;
  }
}

int getChannel(MidiMSG msg){
  return (msg >> 16) &0x0f; // sic.
}

int getNote(MidiMSG msg){
  return (msg >> 8) &0xff;
}

int getVelocity(MidiMSG msg){
  return msg &0xff;
}

int getBend(MidiMSG msg){
  return msg &0xff;
}

int getAftertouch(MidiMSG msg){
  if(getType(msg) == EvtType::POLYPHONIC_AFTERTOUCH){
    return msg &0xff;
  }else{
    return (msg >> 8) &0xff;
  }
}

bool isPanic(MidiMSG msg){
  return (getType(msg) == EvtType::CONTROL) && (((msg >> 8) &0xff) == 0x7b);
}

bool isSustain(MidiMSG msg){
  return (getType(msg) == EvtType::CONTROL) && (((msg >> 8) &0xff) == 0x40);
}

bool isSustainEnable(MidiMSG msg){
  return isSustain(msg) && ((msg &0xff) > 0x40);
}
