#include "nodes/sampler.hpp"

#include <iostream>

#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>


Sampler::Sampler() :
    Node({SocketType::trigger}, {SocketType::audio}, {})
{}

Universe::Descriptor Sampler::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  return Universe::Descriptor();
}

void Sampler::receive_binary(int slot, int length, void* file) {
  SDL_RWops *rw = SDL_RWFromMem(file, length);
  SDL_AudioSpec want, have;
  want.freq = RATE;
  want.format = AUDIO_U16SYS;
  want.channels = 1;
  want.samples = N;

  Uint32 size_;

  SDL_FreeWAV((Uint8*) buff);

  if(SDL_LoadWAV_RW(rw, 1, &want, (Uint8**) &buff, &size_)){
    loaded = true;
    size = size_;
  }else{
    loaded = false;
    buff = nullptr;
    std::cerr << "Sampler: " << SDL_GetError() << std::endl;
  }
  delete [] file;
}

void Sampler::process(NodeInputWindow &input) {
  
}



Sampler::Sampler(){
  SDL_FreeWAV((Uint8*) buff);
}
