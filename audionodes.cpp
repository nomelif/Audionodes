#include <iostream>
#include <vector>
#include <array>
#include <set>
#include <cmath>
#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>

const size_t N = 1024;
const int rate = 44100;
typedef std::array<float, N> Chunk;

class Node {
  struct NodeBundle {
    
  };
  public:
  NodeBundle *bundle;
  virtual std::vector<Chunk> process(std::vector<Chunk>);
  Node() {}
  ~Node() {
    delete bundle;
  }
};

class SineOscillator : Node {
  struct SineOscillatorBundle : NodeBundle {
    float state;
    SineOscillatorBundle(float state) : state(state) {}
  };
  enum InputSocket {
    frequency, amplitude, offset
  };
  public:
  SineOscillator() {
    bundle = new SineOscillatorBundle(0.);
  }
  std::vector<Chunk> process(std::vector<Chunk> input) {
    auto output = std::vector<Chunk>(1, Chunk());
    SineOscillatorBundle *bundle = (SineOscillatorBundle*)this->bundle;
    float state = bundle->state;
    for (size_t i = 0; i < N; ++i) {
      state = std::fmod(state + input[InputSocket::frequency][i]/rate, 1);
      output[0][i] =
        std::sin(state*2*M_PI) * input[InputSocket::amplitude]
        + input[InputSocket::offset];
    }
    bundle->state = state;
    return output;
  }
};

class Sink {
  public:
  std::vector<Chunk> process(std::vector<Chunk> input) {
    return input;
  }
};

class NodeTree {
  std::vector<Node*> nodes;
  public:
  Chunk evaluate() {
    
  }
} *main_node_tree = nullptr;



void audio_callback(void *userdata, Uint8 *_stream, int len) {
  // Cast byte stream into 16-bit signed int stream
  Sint16 *stream = (Sint16*) _stream;
  len /= 2;
  if (len != N) {
    // Horrible failure
  }
  if (main_node_tree == nullptr) {
    for (int i = 0; i < len; ++i) stream[i] = 0;
    return;
  }
  
}

// Methods to be used through the FFI
extern "C" {
  void initialize() {
    SDL_Init(SDL_INIT_AUDIO);
    
		SDL_AudioSpec spec;
		spec.freq     = rate;
		spec.format   = AUDIO_S16SYS;
		spec.channels = 1;
		spec.samples  = N * 2;
		spec.callback = audio_callback;
		spec.userdata = nullptr;
		SDL_AudioSpec obtainedSpec;
		SDL_OpenAudio(&spec, &obtainedSpec);
		SDL_PauseAudio(0); 
  }
  
  void cleanup() {
    SDL_CloseAudio();
  }
}
