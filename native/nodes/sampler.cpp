#include "nodes/sampler.hpp"

#include <iostream>

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
  delete [] buff;
  buff = nullptr;

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
    buff = new float[size];
    for (size_t i = 0; i < size; i++) {
      buff[i] = ((float*) cvt.buf)[i];
    }
    delete [] cvt.buf;
    loaded = true;
  } else {
    loaded = false;
    buff = nullptr;
    std::cerr << "Sampler: " << SDL_GetError() << std::endl;
  }
  delete [] ((char*) file);
  playhead = 0;
  if(get_property_value(Properties::mode) == 0 || loaded == false)
    running = false;
  else
    running = true;
}

void Sampler::process(NodeInputWindow &input) {

  // Trigger detection
  auto &triggers = input[InputSockets::trigger_socket].get<TriggerData>();
  if (triggers.events.size() > 0){
    if(get_property_value(Properties::mode) == 0){
      playhead = 0;
      running = true;
    }else{
      playhead = 0;
      running = !running;
    }
  }

  Chunk &value = output_window[0].mono;

  // If no file is loaded or the file is not being played, send an empty signal
  if (!loaded || !running || playhead > size) {
    value.fill(0);
  } else {
    // Read from the file either until the end of the chunk or until the end of the file
    for (size_t j = 0; j < N; ++j) {
      value[j] = buff[(playhead + j)%size];
    }

    // Fill the rest with zeroes
    if (size-playhead < N && get_property_value(Properties::mode) == 0) {
      for (size_t j = size-playhead; j < N; ++j) value[j] = 0;
    }

    // Advance the playhead and maybe end playback
    playhead += N;
    if (playhead >= size) {
      if(get_property_value(Properties::mode) == 0){
        playhead = 0;
        running = false;
      }else
        playhead = playhead % size;
    }
  }

}

Sampler::~Sampler(){
  delete [] buff;
}

}
