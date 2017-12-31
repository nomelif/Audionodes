#include "node_tree.hpp"

NodeTree::Link::Link(bool connected, size_t node, size_t socket) :
  connected(connected),
  from_node(node),
  from_socket(socket)
{}


NodeTree::NodeTree(std::vector<Node*> order, std::vector<std::vector<Link>> links) :
  amount(order.size()),
  node_evaluation_order(order),
  links(links)
{
  prepare_polyphony_universes();
}

void NodeTree::prepare_polyphony_universes() {
  node_polyphony_descriptors.reserve(amount);
  for (size_t i = 0; i < amount; ++i) {
    Node *node = node_evaluation_order[i];
    std::vector<Universe::Pointer> inputs;
    inputs.reserve(node->get_input_count());
    for (Link link : links[i]) {
      if (link.connected) {
        inputs.push_back(node_polyphony_descriptors[link.from_node].output);
      } else {
        inputs.emplace_back(new Universe());
      }
    }
    node_polyphony_descriptors.push_back(node->infer_polyphony_operation(inputs));
  }
}

Chunk NodeTree::evaluate() {
  std::vector<NodeOutputWindow> node_outputs; node_outputs.reserve(amount);
  Chunk output;
  output.fill(0.);
  for (size_t i = 0; i < amount; ++i) {
    Node *node = node_evaluation_order[i];
    // Collect node inputs
    size_t input_amt = node->get_input_count();
    NodeInputWindow::SocketsList inputs; inputs.reserve(input_amt);
    for (size_t j = 0; j < input_amt; ++j) {
      Data *socket_data;
      bool view_collapsed = false;
      bool temporary_data = false;
      Link link = links[i][j];
      if (link.connected) {
        socket_data = &node_outputs[link.from_node][link.from_socket];
        // The data will be viewed as collapsed if the chosen universes aren't compatible
        view_collapsed =
          *node_polyphony_descriptors[i].input
          != *node_polyphony_descriptors[link.from_node].output;
      } else {
        // TODO: Don't do this if the input socket isn't audio
        // Interpolate earlier value and new value
        float old_v = node->old_input_values[j];
        float new_v = node->get_input_value(j);
        Chunk audio;
        if (old_v == new_v) audio.fill(new_v);
        else {
          for (size_t k = 0; k < N; ++k) {
            audio[k] = ((N-k-1)*old_v + (k+1)*new_v)/N;
          }
          node->old_input_values[j] = new_v;
        }
        // ~NodeInputWindow handles delete
        socket_data = new AudioData(audio);
        view_collapsed = true;
        temporary_data = true;
      }
      inputs.emplace_back(*socket_data, view_collapsed, temporary_data);
    }
    // Process node
    NodeInputWindow input_window(inputs, node_polyphony_descriptors[i]);
    node->apply_bundle_universe_changes(*node_polyphony_descriptors[i].bundles);
    node_outputs.push_back(std::move(node->process(input_window)));
    if (node->get_is_sink()) {
      const AudioData &data = inputs[0].get<AudioData>();
      for (size_t j = 0; j < N; ++j) {
        output[j] += data.mono[j];
      }
    }
  }
  return output;
}
