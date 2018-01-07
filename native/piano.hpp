
#ifndef PIANO_HPP
#define PIANO_HPP

#include "common.hpp"
#include "node.hpp"
#include "midi_data.hpp"
#include <cmath>

class Piano : public Node {
  enum InputSockets {
    midi_in, sustain_time
  };
  enum OutputSockets {
    frequency, velocity, runtime, decay
  };
  struct VoiceState {
    unsigned char note;
    SigT freq, velocity;
    unsigned long long age = 0, since_rel = 0;
    bool released = false;
    bool dead = false;
  };
  std::vector<VoiceState> voices;
  // null when note doesn't exist, otherwise pointer to VoiceState
  std::array<VoiceState*, 127> existing_note;
  bool sustain = false;
  public:
  Piano();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  NodeOutputWindow process(NodeInputWindow&);
};

#endif
