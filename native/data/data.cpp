#include "data/data.hpp"

Data::~Data() {}
Data Data::dummy = Data();

void AudioData::make_collapsed_version() {
  mono.fill(0);
  for (const Chunk &channel : poly) {
    for (size_t i = 0; i < N; ++i) {
      mono[i] += channel[i];
    }
  }
}

AudioData::AudioData(bool init, size_t reserve) {
  if (init) mono.fill(0);
  poly.reserve(reserve);
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

AudioData::PolyWriter::PolyWriter(AudioData &bind) :
  bind(bind),
  internal(bind.poly)
{}

AudioData::PolyWriter::PolyWriter(AudioData &bind, size_t size) :
  bind(bind),
  internal(bind.poly)
{
  resize(size);
}

AudioData::PolyWriter::~PolyWriter() {
  bind.make_collapsed_version();
}

