#include "microphone.hpp"
#include <iostream>

namespace audionodes {

static NodeTypeRegistration<Microphone> registration("MicrophoneNode");

void Microphone::callback(void *userdata, Uint8 *_stream, int len) {
  Microphone *node = (Microphone*) userdata;
  if (!node->mark_connected) return;
  float *stream = (float*)_stream;
  len /= sizeof(float);
  int amt = len/N;
  int si = 0;
  for (int i = 0; i < amt; i++) {
    Chunk buf;
    for (size_t j = 0; j < N && si < len; ++j, ++si) {
      buf[j] = stream[si];
    }
    node->q.push(buf);
  }
}

Microphone::Microphone() :
    Node({}, {SocketType::audio}, {})
{
  open();
}
Microphone::Microphone(Microphone &other) :
    Node(other)
{
  open();
}

Microphone::~Microphone() {
  SDL_CloseAudioDevice(dev);
}

void Microphone::open() {
  SDL_AudioSpec want, have;

  want.freq = RATE;
  want.format = AUDIO_F32SYS;
  want.channels = 1;
  want.samples = N;
  want.callback = callback;
  want.userdata = this;
  
  dev = SDL_OpenAudioDevice(NULL, true, &want, &have, 0);

  if (dev == 0) {
    std::cerr << "Failed to open microphone: " << SDL_GetError() << std::endl;
  }
  SDL_PauseAudioDevice(dev, 0);
}

void Microphone::connect_callback() {
  q.clear();
}

void Microphone::process(NodeInputWindow &input) {
  Chunk &output = output_window[0].mono;
  if (!q.empty()) {
    output = q.pop();
  } else {
    output.fill(0);
  }
}

}
