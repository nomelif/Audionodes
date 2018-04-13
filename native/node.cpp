#include "node.hpp"
#include "data/midi.hpp"

Node::Node(
  SocketTypeList input_types, SocketTypeList output_types,
  PropertyTypeList property_types, bool is_sink) :
    is_sink(is_sink),
    _input_socket_types(input_types),
    _output_socket_types(output_types),
    _property_types(property_types),
    input_socket_types(_input_socket_types),
    output_socket_types(_output_socket_types),
    property_types(_property_types)
{
  input_values.resize(input_types.size());
  old_input_values.resize(input_types.size());
  property_values.resize(property_types.size());
  output_window.sockets.reserve(input_types.size());
  for (auto type : output_types) {
    Data *data;
    switch (type) {
      typedef SocketType ST;
      case ST::audio:
        data = new AudioData();
        break;
      case ST::midi:
        data = new MidiData();
        break;
    }
    Data **data_ptr = new Data*(data);
    output_window.sockets.push_back(data_ptr);
  }
}

Node::~Node() {}

bool Node::get_is_sink() { return is_sink; }
size_t Node::get_input_count() { return input_socket_types.size(); }

void Node::set_input_value(int index, SigT value) {
  input_values[index] = value;
}
SigT Node::get_input_value(int index) {
  return input_values[index];
}
void Node::set_property_value(int index, int value) {
  property_values[index] = value;
}
int Node::get_property_value(int index) {
  return property_values[index];
}
void Node::receive_binary(int, int, void*) {}

void Node::connect_callback() {}
void Node::disconnect_callback() {}

void Node::copy_input_values(const Node &old_node) {
  input_values = old_node.input_values;
  old_input_values = old_node.old_input_values;
  property_values = old_node.property_values;
}

Universe::Descriptor Node::infer_polyphony_operation(std::vector<Universe::Pointer> inputs) {
  Universe::Descriptor result;
  // Universes will be the first polyphonic universe found in the inputs,
  // otherwise monophonic
  for (auto uni : inputs) {
    if (uni->is_polyphonic()) {
      result.set_all(uni);
      break;
    }
  }
  return result;
}

void Node::apply_bundle_universe_changes(const Universe&) {}
