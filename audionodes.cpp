#include <iostream>
#include <vector>
#include <array>
#include <map>
#include <cmath>
#include <atomic>
#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>

const size_t N = 1024;
const int rate = 44100;
typedef std::array<float, N> Chunk;

class Node {
  bool mark_deletion = false;
  protected:
  bool is_sink = false;
  size_t input_count, output_count;
  std::vector<std::atomic<float>> input_values;
  public:
  std::vector<float> old_input_values;
  bool get_is_sink() { return is_sink; }
  size_t get_input_count() { return input_count; }
  void set_input_value(int index, float value) {
    // In order to be thread-safe, the vector may never be resized, only its elements assigned to
    input_values[index] = value;
  }
  float get_input_value(int index) {
    return input_values[index];
  }
  virtual std::vector<Chunk> process(std::vector<Chunk>);
  Node() {}
  ~Node() {}
};

class SineOscillator : Node {
  float state = 0.;
  enum InputSocket {
    frequency, amplitude, offset
  };
  public:
  SineOscillator() : input_count(3), output_count(1) {
    input_values.resize(input_count);
    old_input_values.resize(input_count);
  }
  void resetState() {
    state = 0.;
  }
  std::vector<Chunk> process(std::vector<Chunk> input) {
    auto output = std::vector<Chunk>(1, Chunk());
    for (size_t i = 0; i < N; ++i) {
      state = std::fmod(state + input[InputSocket::frequency][i]/rate, 1);
      output[0][i] =
        std::sin(state*2*M_PI) * input[InputSocket::amplitude][i]
        + input[InputSocket::offset][i];
    }
    return output;
  }
};

class Sink : Node {
  public:
  Sink() : is_sink(true), input_count(1), output_count(0) {
    input_values.resize(input_count);
    old_input_values.resize(input_count);
  }
  std::vector<Chunk> process(std::vector<Chunk> input) {
    return input;
  }
};

// Nodes addressed by unique integer pointer-values
// (in Blender these are is from .as_pointer())
std::map<intptr_t, Node*> node_storage;

class NodeTree {
  public:
  struct Link {
    bool connected;
    size_t from_node, from_socket;
  }
  private:
  std::vector<Node*> node_evaluation_order;
  std::vector<std::vector<Link>> links; // Link-edges to each node
  public:
  Chunk evaluate() {
    size_t amount = node_evaluation_order.size();
    std::vector<std::vector<Chunk>> node_outputs(amount);
    Chunk output;
    for (size_t i = 0; i < amount; ++i) {
      Node *node = node_evaluation_order[i];
      // Collect node inputs
      std::vector<Chunk> inputs(node->get_input_count());
      for (size_t j = 0; j < node->get_input_count(); ++j) {
        Link link = links[i][j];
        if (link.connected) {
          inputs[j] = node_outputs[link.from_node][link.from_socket];
        } else {
          // Interpolate earlier value and new value
          float old_v = node->old_input_values[j];
          float new_v = node->get_input_value(j);
          for (size_t k = 0; k < N; ++k) {
            inputs[j][k] = ((N-k-1)*old_v + (k+1)*new_v)/N;
          }
          node->old_input_values[j] = new_v;
        }
      }
      // Process node
      node_outputs[i] = node->process(inputs);
      if (node->get_is_sink()) {
        output = node_outputs[i][0];
      }
    }
    return output;
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
  const Sint16 maximum_value = (1 << 15)-1;
  const Sint16 minimum_value = -(1 << 15);
  Chunk result = main_node_tree->evaluate();
  for (int i = 0; i < len; ++i) {
    if (result[i] < -1) {
      stream[i] = minimum_value;
    } else if (result[i] >= 1) {
      stream[i] = maximum_value;
    } else {
      stream[i] = result[i] * maximum_value;
    }
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
