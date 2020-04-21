#include "audionodes.hpp"

namespace audionodes {

// Each node registers itself here (refer to node.hpp, RegisterNodeType)
NodeTypeMap& get_node_types() {
  static NodeTypeMap node_types;
  return node_types;
}

// Nodes addressed by unique integers
std::map<node_uid, Node*> node_storage;
node_uid node_storage_counter = 0;
node_uid last_node_uid;
node_uid node_storage_alloc() {
  last_node_uid = node_storage_counter++;
  return last_node_uid;
}

NodeTree *main_node_tree;

InboundMessage::InboundMessage() {}
InboundMessage::InboundMessage(Node* node, size_t slot, float audio_input) :
    type(Type::audio_input), node(node), slot(slot), audio_input(audio_input)
{}
InboundMessage::InboundMessage(Node* node, size_t slot, int property) :
    type(Type::property), node(node), slot(slot), property(property)
{}
InboundMessage::InboundMessage(Node* node, size_t slot, int length, void *binary) :
    type(Type::binary), node(node), slot(slot), property(length), binary(binary)
{}

void InboundMessage::apply() {
  switch (type) {
    case Type::audio_input:
      node->set_input_value(slot, audio_input);
      break;
    case Type::property:
      node->set_property_value(slot, property);
      break;
    case Type::binary:
      node->receive_binary(slot, property, binary);
      break;
  }
}

CircularBuffer<InboundMessage, 256> inbd_msg_queue;
CircularBuffer<Node::ReturnMessage, 512> outbd_msg_queue;
std::vector<Node::ReturnMessage> outbd_msg_queue_sync;

static AudionodesReturnMessage convert_return_message(Node::ReturnMessage msg) {
  AudionodesReturnMessage into {true, msg.uid, msg.msg_type, msg.data_type};
  switch (msg.data_type) {
    case 0:
      into.integer = msg.integer;
      break;
    case 1:
      into.number = msg.number;
      break;
  }
  return into;
}

void receive_message(InboundMessage msg) {
  if (msg.node->mark_connected) {
    // Node is connected and actively used by the execution thread, use thread-safe communication
    // Sleep until queue has room
    for (size_t rep = 0; rep < 10 && inbd_msg_queue.full(); ++rep) {
      std::this_thread::sleep_for(std::chrono::milliseconds(long(1000.*N/RATE+1)));
    }
    // Fail
    if (inbd_msg_queue.full()) {
      std::cerr << "Audionodes native: Unable to communicate with execution thread" << std::endl;
      if (msg.type == InboundMessage::Type::binary) {
        char *ptr = (char*) msg.binary;
        delete [] ptr;
      }
      return;
    }
    inbd_msg_queue.push(msg);
  } else {
    // Apply the message directly
    msg.apply();
  }
}

static std::atomic<bool> messages_flushed(false);

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
  while (!inbd_msg_queue.empty()) {
    InboundMessage msg = inbd_msg_queue.pop();
    msg.apply();
  }
  constexpr Sint16 maximum_value = (1 << 15)-1;
  constexpr Sint16 minimum_value = -(1 << 15);
  bool refresh_ui = messages_flushed;
  if (refresh_ui) messages_flushed = false;
  const Chunk &result = main_node_tree->evaluate(refresh_ui);
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

SDL_AudioDeviceID dev;
bool initialized = false;

std::vector<NodeTree::ConstructionLink> tree_update_links;

extern "C" {
  // Internal API
  // extern "C" in anticipation of external add-on nodes. A lot of Node functionality
  // still isn't cross-compiler compatbile so this is not possible yet.
  void audionodes_register_node_type(const char *identifier, Node::Creator creator) {
    get_node_types()[identifier] = creator;
  }
  
  void audionodes_unregister_node_type(const char *identifier) {
    get_node_types().erase(identifier);
  }
  
  node_uid audionodes_get_newest_node_uid() {
    return last_node_uid;
  }
  
  void audionodes_send_return_message(Node::ReturnMessage msg, bool exec_thread) {
    // TODO: Use thread_local or other stuff to detect current thread
    if (exec_thread) {
      outbd_msg_queue.push(msg);
    } else {
      outbd_msg_queue_sync.push_back(msg);
    }
  }
  
  // Methods to be used through the FFI
  void audionodes_initialize() {
    SDL_Init(SDL_INIT_AUDIO);

    SDL_AudioSpec spec;
    spec.freq     = RATE;
    spec.format   = AUDIO_S16SYS;
    spec.channels = 1;
    spec.samples  = N;
    spec.callback = audio_callback;
    spec.userdata = nullptr;
    SDL_AudioSpec obtainedSpec;
    dev = SDL_OpenAudioDevice(NULL, 0, &spec, &obtainedSpec, 0);
    if (dev == 0) {
      std::cerr << "Audionides Native: Unable to open audio device: " << SDL_GetError() << std::endl;
      return;
    }
    if (obtainedSpec.samples == N/2) {
      // The sample rate gets halved on some systems for some reason
      // -> correct for that
      std::cerr << "Audionodes Native: SDL halved sample rate... trying to correct" << std::endl;
      SDL_CloseAudioDevice(dev);
      spec.samples = 2*N;
      obtainedSpec = SDL_AudioSpec();
      dev = SDL_OpenAudioDevice(NULL, 0, &spec, &obtainedSpec, 0);
      if (obtainedSpec.samples != N || dev == 0) {
        std::cerr << "Audionodes Native: Halving correction failed " << SDL_GetError() << std::endl;
        return;
      }
    }
    SDL_PauseAudioDevice(dev, 0);
  }

  void audionodes_cleanup() {
    SDL_CloseAudioDevice(dev);
    for (auto &id_node_pair : node_storage) {
      delete id_node_pair.second;
    }
    node_storage.clear();
    delete main_node_tree;
    main_node_tree = nullptr;
  }

  node_uid audionodes_create_node(const char* type) {
    if (get_node_types().count(type)) {
      node_uid id = node_storage_alloc();
      Node *node = get_node_types().at(type).construct();
      node_storage[id] = node;
      return id;
    } else {
      std::cerr << "Audionodes native: Tried to create node of invalid type \"" << type << "\"" << std::endl;
      return -1;
    }
  }

  node_uid audionodes_copy_node(node_uid old_id, const char* type) {
    Node *old_node;
    if (!node_storage.count(old_id)) {
      std::cerr << "Audionodes native: Tried to copy non-existent node " << old_id << std::endl;
      return -1;
    }
    old_node = node_storage[old_id];
    if (get_node_types().count(type)) {
      node_uid id = node_storage_alloc();
      Node *node = get_node_types().at(type).copy(old_node);
      node_storage[id] = node;
      return id;
    } else {
      std::cerr << "Audionodes native: Tried to copy node of invalid type \"" << type << "\"" << std::endl;
      return -1;
    }
  }

  void audionodes_remove_node(node_uid id) {
    if (!node_storage.count(id)) {
      std::cerr << "Audionodes native: Tried to remove non-existent node " << id << std::endl;
      return;
    }
    node_storage[id]->mark_deletion = true;
  }
  
  bool audionodes_node_exists(node_uid id) {
    return node_storage.count(id);
  }

  void audionodes_update_node_input_value(node_uid id, int input_index, float value) {
    if (!node_storage.count(id)) {
      std::cerr << "Audionodes native: Tried to update input value of non-existent node " << id << std::endl;
      return;
    }
    receive_message(InboundMessage(node_storage[id], input_index, value));
  }

  void audionodes_update_node_property_value(node_uid id, int enum_index, int value) {
    if (!node_storage.count(id)) {
      std::cerr << "Audionodes native: Tried to update property value of non-existent node " << id << std::endl;
      return;
    }
    receive_message(InboundMessage(node_storage[id], enum_index, value));
  }
  
  void audionodes_send_node_binary_data(node_uid id, int slot, int length, void *_bin) {
    if (!node_storage.count(id)) {
      std::cerr << "Audionodes native: Tried to send binary data to non-existent node " << id << std::endl;
      return;
    }
    // Node (or receive_message on failure) will handle deletion
    char *bin = new char[length];
    std::memcpy(bin, _bin, length);
    receive_message(InboundMessage(node_storage[id], slot, length, bin));
  }
  
  AudionodesConfigurationDescriptor* audionodes_get_configuration_options(node_uid id) {
    static Node::ConfigurationDescriptorList configuration_options;
    static std::vector<AudionodesConfigurationDescriptor> configuration_options_C;
    static std::vector<std::vector<const char*>> configuration_strings_C;
    if (!node_storage.count(id)) {
      std::cerr << "Audionodes native: Tried to get configuration options from non-existent node " << id << std::endl;
      configuration_options = {};
    } else {
      configuration_options = node_storage[id]->get_configuration_options();
    }
    configuration_options_C.clear();
    configuration_strings_C.clear();
    for (Node::ConfigurationDescriptor &conf : configuration_options) {
      configuration_strings_C.emplace_back();
      auto &strlist = configuration_strings_C.back();
      strlist.reserve(conf.available_values.size()+1);
      for (auto &str : conf.available_values) {
        strlist.push_back(str.c_str());
      }
      strlist.push_back(nullptr);
      configuration_options_C.push_back({true,
        conf.name.c_str(),
        conf.current_value.c_str(),
        strlist.data()
      });
    }
    // List end indicator
    configuration_options_C.push_back({false, nullptr, nullptr, nullptr});
    return configuration_options_C.data();
  }
  
  int audionodes_set_configuration_option(node_uid id, const char *name, const char *option) {
    if (!node_storage.count(id)) {
      std::cerr << "Audionodes native: Tried to set configuration option of non-existent node " << id << std::endl;
      return -1;
    }
    return node_storage[id]->set_configuration_option(std::string(name), std::string(option));
  }
  
  AudionodesReturnMessage* audionodes_fetch_messages() {
    static std::vector<AudionodesReturnMessage> messages_C;
    messages_C.clear();
    for (auto &msg : outbd_msg_queue_sync) {
      messages_C.push_back(convert_return_message(msg));
    }
    outbd_msg_queue_sync.clear();
    for (size_t rep = 0; rep < 512; ++rep) {
      if (outbd_msg_queue.empty()) break;
      messages_C.push_back(convert_return_message(outbd_msg_queue.pop()));
    }
    messages_C.push_back({false, -1, 0});
    messages_flushed = true;
    return messages_C.data();
  }
  
  void audionodes_begin_tree_update() {
    tree_update_links.clear();
  }

  void audionodes_add_tree_update_link(node_uid from_node, node_uid to_node, size_t from_socket, size_t to_socket) {
    if (!node_storage.count(from_node) || !node_storage.count(to_node)) {
      std::cerr << "Audionodes native: Tried to create a link to/from non-existent node " << from_node << " " << to_node << std::endl;
      return;
    }
    tree_update_links.push_back({from_node, to_node, from_socket, to_socket});
  }

  void audionodes_finish_tree_update() {
    std::map<node_uid, std::vector<NodeTree::ConstructionLink>> links_to;
    std::map<node_uid, int> links_from_count;
    for (auto link : tree_update_links) {
      links_to[link.to_node].push_back(link);
    }
    // Breadth first search from sinks to find reverse topological order
    std::vector<node_uid> q;
    std::vector<node_uid> marked_for_deletion;
    // will contain all nodes that need to be evaluated (directly or indirectly connected to a sink)
    std::set<node_uid> to_process;
    std::vector<node_uid> to_process_q;
    for (auto &id_node_pair : node_storage) {
      if (id_node_pair.second->mark_deletion) {
        marked_for_deletion.push_back(id_node_pair.first);
      } else {
        if (id_node_pair.second->get_is_sink()) {
          q.push_back(id_node_pair.first);
          to_process.insert(id_node_pair.first);
          to_process_q.push_back(id_node_pair.first);
        }
      }
    }
    for (size_t i = 0; i < to_process_q.size(); ++i) {
      node_uid id = to_process_q[i];
      for (auto link : links_to[id]) {
        if (node_storage[link.from_node]->mark_deletion) continue;
        links_from_count[link.from_node]++;
        if (to_process.count(link.from_node)) continue;
        to_process.insert(link.from_node);
        to_process_q.push_back(link.from_node);
      }
    }
    for (size_t i = 0; i < q.size(); ++i) {
      node_uid id = q[i];
      for (auto link : links_to[id]) {
        if (!to_process.count(link.from_node)) continue;
        links_from_count[link.from_node]--;
        if (links_from_count[link.from_node] == 0) {
          q.push_back(link.from_node);
        }
      }
    }
    if (q.size() < to_process.size()) {
      // Not all nodes that were supposed to be included got into the order ->
      // there is a loop
      std::cerr << "Audionodes native: Error building tree: loop found" << std::endl;
      tree_update_links.clear();
      return;
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
        if (!to_process.count(link.from_node)) continue;
        final_links[i][link.to_socket] = NodeTree::Link(true, node_index[link.from_node], link.from_socket);
      }
    }

    // Call callbacks on newly connected nodes
    for (Node *node : final_order) {
      if (!node->mark_connected) {
        node->mark_connected = true;
        node->connect_callback();
      }
      node->_tmp_connected = true;
    }

    // Make a new node tree with the newly acquired evaluation parameters
    NodeTree *new_node_tree = new NodeTree(final_order, final_links);
    NodeTree *old_node_tree = main_node_tree;
    // Substitute the active node tree safely
    SDL_LockAudioDevice(dev);
    main_node_tree = new_node_tree;
    SDL_UnlockAudioDevice(dev);
    delete old_node_tree;

    // Call callbacks on newly disconnected nodes
    for (auto &id_node_pair : node_storage) {
      Node *node = id_node_pair.second;
      if (!node->_tmp_connected && node->mark_connected) {
        node->mark_connected = false;
        node->disconnect_callback();
      }
      node->_tmp_connected = false;
    }

    // Lastly, we clean up the removed nodes
    for (node_uid id : marked_for_deletion) {
      Node *node = node_storage[id];
      delete node;
      node_storage.erase(id);
    }

    tree_update_links.clear();
    tree_update_links.shrink_to_fit();
  }
}

}
