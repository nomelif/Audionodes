
#ifndef PIANO_HPP
#define PIANO_HPP

#include "common.hpp"
#include "node.hpp"
#include "data/midi.hpp"
#include <cmath>

namespace audionodes {

class Piano : public Node {
  enum InputSockets {
    midi_in, decay_time
  };
  enum OutputSockets {
    frequency, velocity, runtime, decay
  };
  struct VoiceState {
    unsigned char note;
    SigT freq, velocity;
    unsigned long long age = 0, decaying_for = 0;
    enum class Stage {
      active, decaying, dead
    } stage;
    bool released = false;
  };
  using VoiceStage = VoiceState::Stage;
  std::vector<VoiceState> voices, new_voices, voices_tmp;
  std::vector<size_t> removed_tmp;
  // null when note doesn't exist, otherwise pointer to VoiceState
  std::array<VoiceState*, 128> existing_note;
  bool sustain = false;
  bool sostenuto = false;
  std::array<bool, 128> sostenuto_mask;
  inline bool should_decay(const VoiceState &voice) {
    return voice.released
      && voice.stage == VoiceStage::active
      && !sustain
      && !(sostenuto && sostenuto_mask[voice.note]);
  }
  void check_all_decay();
  public:
  Piano();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>) override;
  void process(NodeInputWindow&) override;
};

}

#endif
