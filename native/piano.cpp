#include "piano.hpp"

Piano::Piano() :
    Node({SocketType::midi, SocketType::audio}, SocketTypeList(4, SocketType::audio), {})
{
  existing_note.fill(nullptr);
}

Universe::Descriptor Piano::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  Universe::Pointer mono(new Universe()), uni(new Universe(true, voices.size()));
  return Universe::Descriptor(mono, mono, uni);
}

NodeOutputWindow Piano::process(NodeInputWindow &input) {
  input.universes.output->ensure(voices.size());
  const MidiData &midi = input[InputSockets::midi_in].get<MidiData>();
  SigT sust = std::max(SigT(0), input[InputSockets::sustain_time][0][0]);
  std::vector<VoiceState> new_voices;
  for (const MidiData::Event event : midi.events) {
    unsigned char note = event.get_note();
    switch (event.get_type()) {
      case MidiData::EType::note_on:
        if (existing_note[note]) {
          existing_note[note]->released = true;
          if (sust == 0) existing_note[note]->dead = true;
        }
        new_voices.push_back({note, SigT(std::pow(2, (note-69)/12.)*440), event.get_velocity()/SigT(127)});
        existing_note[note] = &new_voices.back();
        break;
      case MidiData::EType::note_off:
        if (existing_note[note]) {
          existing_note[note]->released = true;
          if (sust == 0) existing_note[note]->dead = true;
        }
        break;
      case MidiData::EType::control:
        break;
      default:
        break;
    }
  }
  std::vector<size_t> removed;
  std::vector<VoiceState> voices_tmp;
  for (size_t i = 0; i < voices.size(); ++i) {
    if (voices[i].released && voices[i].since_rel > size_t(sust*rate)) {
      voices[i].dead = true;
    }
    if (voices[i].dead) {
      removed.push_back(i);
    } else {
      voices_tmp.push_back(voices[i]);
    }
  }
  input.universes.output->update(removed, new_voices.size());
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
  AudioData::PolyList frequency(n), velocity(n), runtime(n), decay(n);
  for (size_t i = 0; i < n; ++i) {
    VoiceState &voice = voices[i];
    frequency[i].fill(voice.freq);
    velocity[i].fill(voice.velocity);
    for (size_t j = 0; j < N; ++j) {
      runtime[i][j] = SigT(voice.age++)/rate;
    }
    if (voice.released) {
      for (size_t j = 0; j < N; ++j) {
        decay[i][j] = std::max(SigT(0), (sust*rate-SigT(voice.since_rel++))/(sust*rate));
      }
    } else decay[i].fill(1);
  }
  return NodeOutputWindow({new AudioData(frequency), new AudioData(velocity), new AudioData(runtime), new AudioData(decay)});
}
