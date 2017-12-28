#include "data.hpp"

Data::~Data() {}


void AudioData::make_collapsed_version() {
  mono.fill(0);
  for (const Chunk &channel : poly) {
    for (size_t i = 0; i < N; ++i) {
      mono[i] += channel[i];
    }
  }
}

AudioData::AudioData(bool init) {
  if (init) mono.fill(0);
}

AudioData::AudioData(PolyList poly) :
  poly(poly)
{
  make_collapsed_version();
}

AudioData::AudioData(Chunk mono) :
  mono(mono)
{}

AudioData AudioData::dummy = AudioData();

MidiData MidiData::dummy = MidiData();
