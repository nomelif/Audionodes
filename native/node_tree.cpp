#include "node_tree.hpp"

NodeTree::Link::Link(bool connected, size_t node, size_t socket) :
  connected(connected),
  from_node(node),
  from_socket(socket)
{}


NodeTree::NodeTree(std::vector<Node*> order, std::vector<std::vector<Link>> links) :
  amount(order.size()),
  node_evaluation_order(order)
{
  node_inputs.reserve(amount);
  for (size_t i = 0; i < amount; ++i) {
    Node *node = node_evaluation_order[i];
    
    std::vector<Universe::Pointer> input_universes;
    input_universes.reserve(node->get_input_count());
    for (Link link : links[i]) {
      if (link.connected) {
        input_universes.push_back(node_inputs[link.from_node].universes.output);
      } else {
        input_universes.emplace_back(new Universe());
      }
    }
    Universe::Descriptor universes = node->infer_polyphony_operation(input_universes);
    
    NodeInputWindow::SocketsList input_sockets;
    input_sockets.reserve(node->get_input_count());
    for (size_t j = 0; j < node->get_input_count(); ++j) {
      Link link = links[i][j];
      if (link.connected) {
        Data **data = node_evaluation_order[link.from_node]->output_window.ref(link.from_socket);
        // The data will be viewed as collapsed if the chosen universes aren't compatible
        bool view_collapsed = *universes.input != *node_inputs[link.from_node].universes.output;
        input_sockets.emplace_back(data, view_collapsed, false);
      } else {
        Data **tmp_data_ptr = nullptr;
        bool tmp_audio_data = false;
        if (node->input_socket_types[j] == Node::SocketType::audio) {
          // Unconnected audio socket input -> inline value control
          Data *data = new AudioData(true, 0);
          tmp_data_ptr = new Data*(data);
          tmp_audio_data = true;
        }
        input_sockets.emplace_back(tmp_data_ptr, true, tmp_audio_data);
      }
    }
    
    node_inputs.emplace_back(input_sockets, universes);
  }
}

const Chunk& NodeTree::evaluate() {
  output.fill(0.);
  for (size_t i = 0; i < amount; ++i) {
    Node *node = node_evaluation_order[i];
    // Collect node inputs
    size_t input_amt = node->get_input_count();
    for (size_t j = 0; j < input_amt; ++j) {
      if (node_inputs[i][j].tmp_audio_data) {
        // Interpolate earlier value and new value
        float old_v = node->old_input_values[j];
        float new_v = node->get_input_value(j);
        Chunk &audio = node_inputs[i][j].get_write<AudioData>().mono;
        if (old_v == new_v) audio.fill(new_v);
        else {
          for (size_t k = 0; k < N; ++k) {
            audio[k] = ((N-k-1)*old_v + (k+1)*new_v)/N;
          }
          node->old_input_values[j] = new_v;
        }
      }
    }
    // Process node
    node->apply_bundle_universe_changes(*node_inputs[i].universes.bundles);
    node->process(node_inputs[i]);
    if (node->get_is_sink()) {
      const AudioData &data = node_inputs[i][0].get<AudioData>();
      for (size_t j = 0; j < N; ++j) {
        output[j] += data.mono[j];
      }
    }
  }
  return output;
}
