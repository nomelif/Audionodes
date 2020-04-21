#include "node_tree.hpp"

#include "data/trigger.hpp"

namespace audionodes {

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
        // Unconnected input socket -> inline value control
        Data *data = nullptr;
        bool tmp_data = true;
        switch (node->input_socket_types[j]) {
          typedef Node::SocketType ST;
          case ST::audio:
            data = new AudioData(true, 0);
            break;
          case ST::trigger:
            data = new TriggerData();
            break;
          default:
            tmp_data = false;
            break;
        }
        Data **tmp_data_ptr = nullptr;
        if (tmp_data) {
          tmp_data_ptr = new Data*(data);
        }
        input_sockets.emplace_back(tmp_data_ptr, true, tmp_data);
      }
    }
    
    node_inputs.emplace_back(input_sockets, universes);
  }
}

const Chunk& NodeTree::evaluate(bool refresh_ui) {
  output.fill(0.);
  for (size_t i = 0; i < amount; ++i) {
    Node *node = node_evaluation_order[i];
    if (refresh_ui) node->refresh_ui_flag = false;
    // Collect node inputs
    size_t input_amt = node->get_input_count();
    for (size_t j = 0; j < input_amt; ++j) {
      if (node_inputs[i][j].tmp_data) {
        SigT old_v = node->old_input_values[j];
        SigT new_v = node->input_values[j];
        switch (node->input_socket_types[j]) {
          typedef Node::SocketType ST;
          case ST::audio: {
            // Interpolate earlier value and new value
            Chunk &audio = node_inputs[i][j].get_write<AudioData>().mono;
            if (old_v == new_v) audio.fill(new_v);
            else {
              for (size_t k = 0; k < N; ++k) {
                audio[k] = ((N-k-1)*old_v + (k+1)*new_v)/N;
              }
            }
          } break;
          case ST::trigger: {
            TriggerData &trigger = node_inputs[i][j].get_clear<TriggerData>();
            if (new_v == 1) {
              trigger.events.push_back(0);
            } else if (new_v == 2) {
              trigger.reset = true;
            }
            node->input_values[j] = 0;
          } break;
          default:
            break;
        }
        node->old_input_values[j] = new_v;
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

}
