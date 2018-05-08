#include "microphone.hpp"
#include <iostream>

void callback(void *userdata, Uint8 *stream, int len) {
  for(int i = 0; i < len; i++){
    ((Microphone*) userdata)->q.push(((SigT) stream[i]) / 128 - 1);
    std::cout << (int) stream[i] << "\n";
  }
}

Microphone::Microphone() :
    Node({}, {SocketType::audio}, {}) {
    SDL_AudioDeviceID dev;

    SDL_AudioSpec want, have;

    SDL_zero(want);
    want.freq = 44100;
    want.format = AUDIO_S16SYS;
    want.channels = 1;
    want.samples = 1024;
    want.callback = callback;
    want.userdata = this;
    
    dev = SDL_OpenAudioDevice(SDL_GetAudioDeviceName(0, 1), 1, &want, &have, 0);

    if (have.format != want.format) {
        SDL_Log("We didn't get the wanted format.");
    }

    SDL_PauseAudioDevice(dev, 0);

    if (dev == 0) {
        SDL_Log("Failed to open audio: %s", SDL_GetError());
    }

    printf("Started at %u\n", SDL_GetTicks());
}

void Microphone::process(NodeInputWindow &input) {
  AudioData::PolyWriter output(output_window[0], 1);
  for(size_t j = 0; j < N; ++j){
    if(q.size() > 0){
      output[0][j] = q.back();
      q.pop();
    }else{
      output[0][j] = 0;
    }
  }
}
