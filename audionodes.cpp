#include <iostream>
#include <vector>
#include <array>
#include <map>
#include <cmath>
#include <mutex>
#include <iostream>
#include <algorithm>
#include <SDL2/SDL.h>
#include <SDL2/SDL_audio.h>

const size_t N = 1024;
const int rate = 44100;
typedef std::array<float, N> Chunk;

class Node {
  protected:
  bool is_sink = false;
  size_t input_count, output_count;
  std::vector<float> input_values;
  std::mutex input_values_mutex;
  public:
  bool mark_deletion = false;
  std::vector<float> old_input_values;
  bool get_is_sink() { return is_sink; }
  size_t get_input_count() { return input_count; }
  void set_input_value(int index, float value) {
    std::lock_guard<std::mutex> lock(input_values_mutex);
    input_values[index] = value;
  }
  float get_input_value(int index) {
    std::lock_guard<std::mutex> lock(input_values_mutex);
    return input_values[index];
  }
  void copy_input_values(Node *old_node) {
    input_values = old_node->input_values;
    old_input_values = old_node->old_input_values;
  }
  virtual std::vector<Chunk> process(std::vector<Chunk>);
  Node(size_t input_count, size_t output_count, bool is_sink=false) :
      is_sink(is_sink),
      input_count(input_count),
      output_count(output_count)
  {
    input_values.resize(input_count);
    old_input_values.resize(input_count);
  }
  virtual ~Node() {}
};

class SineOscillator : public Node {
  float state = 0.;
  enum InputSocket {
    frequency, amplitude, offset
  };
  public:
  const static int type_id = 0;
  SineOscillator() : Node(3, 1) {}
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

class Sink : public Node {
  public:
  const static int type_id = 1;
  Sink() : Node(1, 0, true) {}
  std::vector<Chunk> process(std::vector<Chunk> input) {
    return input;
  }
};

// Nodes addressed by unique integers
typedef int node_uid;
std::map<node_uid, Node*> node_storage;
node_uid node_storage_alloc() {
  if (node_storage.size()) {
    return node_storage.rbegin()->first+1;
  } else {
    return 0;
  }
}

class NodeTree {
  public:
  struct ConstructionLink { // Used when building a new NodeTree on update
    node_uid from_node, to_node;
    size_t from_socket, to_socket;
  };
  struct Link { // Used during execution
    bool connected;
    size_t from_node, from_socket;
    Link(bool connected=false, size_t node=0, size_t socket=0) :
      connected(connected),
      from_node(node),
      from_socket(socket)
    {}
  };
  private:
  std::vector<Node*> node_evaluation_order;
  std::vector<std::vector<Link>> links; // Link-edges to each node
  public:
  NodeTree(std::vector<Node*> order, std::vector<std::vector<Link>> links) :
    node_evaluation_order(order),
    links(links)
  {}
  Chunk evaluate() {
    size_t amount = node_evaluation_order.size();
    std::vector<std::vector<Chunk>> node_outputs(amount);
    Chunk output;
    output.fill(0.);
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
        for (size_t j = 0; j < N; ++j) output[j] += node_outputs[i][0][j];
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
    std::cerr << "Audionodes native: Unexpected sample count: " << len << std::endl;
    return;
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
		spec.samples  = N;
		spec.callback = audio_callback;
		spec.userdata = nullptr;
		SDL_AudioSpec obtainedSpec;
		SDL_OpenAudio(&spec, &obtainedSpec);
		SDL_PauseAudio(0); 
  }
  
  void cleanup() {
    SDL_CloseAudio();
    for (auto &id_node_pair : node_storage) {
      delete id_node_pair.second;
    }
    node_storage.clear();
    delete main_node_tree;
  }
  
  node_uid create_node(int type) {
    node_uid id = node_storage_alloc();
    Node *node;
    switch (type) {
      case SineOscillator::type_id:
        node = new SineOscillator();
        break;
      case Sink::type_id:
        node = new Sink();
        break;
      default:
        std::cerr << "Audionodes native: Tried to create invalid node type" << std::endl;
        return -1;
    }
    node_storage[id] = node;
    return id;
  }
  
  node_uid copy_node(node_uid old_id, int type) {
    node_uid new_id = create_node(type);
    node_storage[new_id]->copy_input_values(node_storage[old_id]);
    return new_id;
  }
  
  void remove_node(node_uid id) {
    if (!node_storage.count(id)) {
      std::cerr << "Audionodes native: Tried to remove non-existent node " << id << std::endl;
      return;
    }
    node_storage[id]->mark_deletion = true;
  }
  
  void update_node_input_value(node_uid id, int input_index, float value) {
    if (!node_storage.count(id)) {
      std::cerr << "Audionodes native: Tried to update input value of non-existent node " << id << std::endl;
      return;
    }
    node_storage[id]->set_input_value(input_index, value);
  }
  
  std::vector<NodeTree::ConstructionLink>* begin_tree_update() {
    std::vector<NodeTree::ConstructionLink> *links;
    links = new std::vector<NodeTree::ConstructionLink>();
    return links;
  }
  
  void add_tree_update_link(std::vector<NodeTree::ConstructionLink> *links, node_uid from_node, node_uid to_node, size_t from_socket, size_t to_socket) {
    if (!node_storage.count(from_node) || !node_storage.count(to_node)) {
      std::cerr << "Audionodes native: Tried to create a link to/from non-existent node " << from_node << " " << to_node << std::endl;
    }
    links->push_back({from_node, to_node, from_socket, to_socket});
  }
  
  void finish_tree_update(std::vector<NodeTree::ConstructionLink> *links) {
    std::map<node_uid, std::vector<NodeTree::ConstructionLink>> links_to;
    std::map<node_uid, int> links_from_count;
    for (auto link : *links) {
      links_to[link.to_node].push_back(link);
      links_from_count[link.from_node]++;
    }
    // Breadth first search from sinks to find reverse topological order
    std::vector<node_uid> q;
    std::vector<node_uid> marked_for_deletion;
    for (auto &id_node_pair : node_storage) {
      if (id_node_pair.second->mark_deletion) {
        marked_for_deletion.push_back(id_node_pair.first);
      }
      if (id_node_pair.second->get_is_sink() && !id_node_pair.second->mark_deletion) {
        q.push_back(id_node_pair.first);
      }
    }
    for (size_t i = 0; i < q.size(); ++i) {
      node_uid id = q[i];
      for (auto link : links_to[id]) {
        if (node_storage[link.from_node]->mark_deletion) continue;
        links_from_count[link.from_node]--;
        if (links_from_count[link.from_node] == 0) {
          q.push_back(link.from_node);
        }
      }
    }
    // Reverse the resulting vector to have the correct evaluation order
    std::reverse(q.begin(), q.end());
    
    // Collect final evaluation order and links
    std::vector<Node*> final_order(q.size());
    std::vector<std::vector<NodeTree::Link>> final_links(q.size());
    std::map<node_uid, size_t> node_index;
    for (size_t i = 0; i < q.size(); ++i) {
      node_uid id = q[i];
      node_index[id] = i;
      Node *node = node_storage[id];
      final_order[i] = node;
      final_links[i] = std::vector<NodeTree::Link>(node->get_input_count());
      for (auto link : links_to[id]) {
        final_links[i][link.to_socket] = NodeTree::Link(true, node_index[link.from_node], link.from_socket);
      }
    }
    
    // Make a new node tree with the newly acquired evaluation parameters
    NodeTree *new_node_tree = new NodeTree(final_order, final_links);
    // Substitute the active node tree safely
    SDL_LockAudio();
    delete main_node_tree;
    main_node_tree = new_node_tree;
    SDL_UnlockAudio();
    
    // Lastly, we clean up the removed nodes
    for (node_uid id : marked_for_deletion) {
      Node *node = node_storage[id];
      delete node;
      node_storage.erase(id);
    }
  }
}
