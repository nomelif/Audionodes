#include "node_tree.hpp"

NodeTree::Link::Link(bool connected, size_t node, size_t socket) :
  connected(connected),
  from_node(node),
  from_socket(socket)
{}


NodeTree::NodeTree(std::vector<Node*> order, std::vector<std::vector<Link>> links) :
  node_evaluation_order(order),
  links(links)
{}

Chunk NodeTree::evaluate() {
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
