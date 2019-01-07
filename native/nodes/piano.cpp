#include "nodes/piano.hpp"

namespace audionodes {

static NodeTypeRegistration<Piano> registration("PianoNode");

Piano::Piano() :
    Node({SocketType::midi, SocketType::audio}, SocketTypeList(4, SocketType::audio), {})
{
  existing_note.fill(nullptr);
  sostenuto_mask.fill(false);
}

Universe::Descriptor Piano::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  Universe::Pointer mono(new Universe()), uni(new Universe(true, voices.size()));
  return Universe::Descriptor(mono, mono, uni);
}

void Piano::process(NodeInputWindow &input) {
  input.universes.output->ensure(voices.size());
  const MidiData &midi = input[InputSockets::midi_in].get<MidiData>();
  SigT decay_time = std::max(SigT(0), input[InputSockets::decay_time][0][0]);
  new_voices.clear();
  for (const MidiData::Event event : midi.events) {
    unsigned char note = event.get_note();
    switch (event.get_type()) {
      using ET = MidiData::EType;
      case ET::note_on:
        if (existing_note[note]) {
          existing_note[note]->released = true;
          existing_note[note]->stage = VoiceStage::decaying;
        }
        new_voices.push_back({note, SigT(std::pow(2, (note-69)/12.)*440), event.get_velocity()/SigT(127)});
        existing_note[note] = &new_voices.back();
        if (!sostenuto) sostenuto_mask[note] = true;
        break;
      case ET::note_off:
        if (existing_note[note]) {
          existing_note[note]->released = true;
          if (!sostenuto) sostenuto_mask[note] = false;
          if (should_decay(*existing_note[note])) {
            existing_note[note]->stage = VoiceStage::decaying;
          }
        }
        break;
      case ET::control:
        if (event.is_panic()) {
          for (auto &voice : voices) {
            voice.stage = VoiceStage::dead;
          }
          for (auto &voice : new_voices) {
            voice.stage = VoiceStage::dead;
          }
        } else if (event.is_sustain()) {
          sustain = event.is_pedal_down();
          if (!sustain) check_all_decay();
        } else if (event.is_sostenuto()) {
          sostenuto = event.is_pedal_down();
          if (!sostenuto) {
            check_all_decay();
            sostenuto_mask.fill(false);
            for (auto &voice : voices) {
              if (!voice.released) sostenuto_mask[voice.note] = true;
            }
            for (auto &voice : new_voices) {
              if (!voice.released) sostenuto_mask[voice.note] = true;
            }
          }
        }
        break;
      default:
        break;
    }
  }
  removed_tmp.clear();
  voices_tmp.clear();
  for (size_t i = 0; i < voices.size(); ++i) {
    if (voices[i].stage == VoiceStage::decaying && voices[i].decaying_for >= size_t(decay_time*RATE)) {
      voices[i].stage = VoiceStage::dead;
    }
    if (voices[i].stage == VoiceStage::dead) {
      removed_tmp.push_back(i);
    } else {
      voices_tmp.push_back(voices[i]);
    }
  }
  input.universes.output->update(removed_tmp, new_voices.size());
  voices.clear();
  size_t n = voices_tmp.size() + new_voices.size();
  voices.reserve(n);
  existing_note.fill(nullptr);
  for (VoiceState voice : voices_tmp) {
    voices.push_back(voice);
    existing_note[voice.note] = &voices.back();
  }
  for (VoiceState voice : new_voices) {
    voices.push_back(voice);
    existing_note[voice.note] = &voices.back();
  }
  AudioData::PolyWriter
    frequency(output_window[OutputSockets::frequency], n),
    velocity(output_window[OutputSockets::velocity], n),
    runtime(output_window[OutputSockets::runtime], n),
    decay(output_window[OutputSockets::decay], n);
  for (size_t i = 0; i < n; ++i) {
    VoiceState &voice = voices[i];
    frequency[i].fill(voice.freq);
    velocity[i].fill(voice.velocity);
    for (size_t j = 0; j < N; ++j) {
      runtime[i][j] = SigT(voice.age++)/RATE;
    }
    if (voice.stage == VoiceStage::decaying) {
      for (size_t j = 0; j < N; ++j) {
        decay[i][j] = std::max(SigT(0), (decay_time*RATE-SigT(voice.decaying_for++))/(decay_time*RATE));
      }
    } else decay[i].fill(1);
  }
}

void Piano::check_all_decay() {
  for (auto &voice : voices) {
    if (should_decay(voice)) {
      voice.stage = VoiceStage::decaying;
    }
  }
  for (auto &voice : new_voices) {
    if (should_decay(voice)) {
      voice.stage = VoiceStage::decaying;
    }
  }
}


}
