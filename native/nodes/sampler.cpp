#include "nodes/sampler.hpp"

namespace audionodes {

static NodeTypeRegistration<Sampler> registration("SamplerNode");

Sampler::Sampler():
 Node({SocketType::trigger}, {SocketType::audio}, {PropertyType::select})
{}

Universe::Descriptor Sampler::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  return Universe::Descriptor();
}

void Sampler::receive_binary(int slot, int length, void* file) {
  SDL_RWops *rw = SDL_RWFromMem(file, length);

  // Temporary to store the size of the input buffer
  Uint32 size_;

  // Delete the old buffer if there was one
  buff.clear();

  // Loads the wave file into tbuf, most probably not with the settings we wanted, have contains the specs of what actually was loaded
  Uint8 *tbuf;
  SDL_AudioSpec have;
  if (SDL_LoadWAV_RW(rw, true, &have, &tbuf, &size_)) {
    // Prepare the conversion from whatever we actually got to SigT mono at our preferred frequency
    SDL_AudioCVT cvt;
    SDL_BuildAudioCVT(&cvt, have.format, have.channels, have.freq, AUDIO_F32SYS, 1, RATE);
    cvt.len = size_;

    // Copy our data over to a buffer big enough to fit both the original and the converted data
    cvt.buf = new Uint8[cvt.len*cvt.len_mult];
    for (int i = 0; i < cvt.len; i++) {
      cvt.buf[i] = tbuf[i];
    }
    SDL_FreeWAV(tbuf);

    // Run the conversion
    SDL_ConvertAudio(&cvt);

    // Copy the data from the temporary buffer to one just large enough
    size = cvt.len_cvt / sizeof(float);
    buff.resize(size);
    for (size_t i = 0; i < size; i++) {
      buff[i] = ((float*) cvt.buf)[i];
    }
    delete [] cvt.buf;
    loaded = true;
  } else {
    loaded = false;
  }
  buff.shrink_to_fit();
  delete [] ((char*) file);
  playhead = 0;
  running = false;
}

void Sampler::process(NodeInputWindow &input) {
  auto &triggers = input[InputSockets::trigger_socket].get<TriggerData>();
  if (triggers.reset) {
    playhead = 0;
    running = false;
  }
  auto &value = output_window[0].mono;
  bool loop = get_property_value(Properties::mode) == Modes::loop;

  if (!loaded || (!running && !triggers.events.size())) {
    value.fill(0);
  } else {
    auto it = triggers.iterate();
    if (loop) {
      for (size_t j = 0; j < N; ++j) {
        size_t trig = it.count(j);
        if (trig) {
          playhead = 0;
          running = running ^ (trig % 2);
        }
        value[j] = running ? buff[playhead] : 0;
        if (++playhead == size) playhead = 0;
      }
    } else {
      for (size_t j = 0; j < N; ++j) {
        if (it.count(j)) {
          playhead = 0;
          running = true;
        }
        value[j] = running ? buff[playhead] : 0;
        if (++playhead == size) running = false;
      }
    }
  }

}

}
