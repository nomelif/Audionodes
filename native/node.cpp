#include "node.hpp"

#include "data/midi.hpp"
#include "data/trigger.hpp"

namespace audionodes {

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
  prepare_output_window();
}

Node::Node(Node &other) :
    is_sink(other.is_sink),
    _input_socket_types(other.input_socket_types),
    _output_socket_types(other.output_socket_types),
    _property_types(other.property_types),
    input_socket_types(_input_socket_types),
    output_socket_types(_output_socket_types),
    property_types(_property_types),
    
    input_values(other.input_values),
    old_input_values(other.old_input_values),
    property_values(other.property_values)
{
  prepare_output_window();
}

void Node::prepare_output_window() {
  output_window.sockets.clear();
  output_window.sockets.reserve(input_socket_types.size());
  for (auto type : output_socket_types) {
    Data *data = nullptr;
    switch (type) {
      typedef SocketType ST;
      case ST::audio:
        data = new AudioData();
        break;
      case ST::midi:
        data = new MidiData();
        break;
      case ST::trigger:
        data = new TriggerData();
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
void Node::set_property_value(int index, int value) {
  property_values[index] = value;
}
int Node::get_property_value(int index) {
  return property_values[index];
}
void Node::receive_binary(int, int, void*) {}

Node::ConfigurationDescriptorList Node::get_configuration_options() { return {}; }
int Node::set_configuration_option(std::string, std::string) { return 0; }

void Node::connect_callback() {}
void Node::disconnect_callback() {}

void Node::copy_input_values(const Node &old_node) {
  input_values = old_node.input_values;
  old_input_values = old_node.old_input_values;
  property_values = old_node.property_values;
}

Universe::Descriptor Node::infer_polyphony_operation(std::vector<Universe::Pointer> inputs) {
  Universe::Pointer poly_uni;
  bool poly_found = false;
  // Universes will be the only polyphonic universe found in the inputs,
  // otherwise (if none or differing) monophonic
  for (auto uni : inputs) {
    if (uni->is_polyphonic()) {
      if (poly_found) {
        if (*poly_uni != *uni) {
          poly_found = false;
          break;
        }
      } else {
        poly_found = true;
        poly_uni = uni;
      }
    }
  }
  if (poly_found) {
    return Universe::Descriptor(poly_uni, poly_uni, poly_uni);
  } else {
    return Universe::Descriptor();
  }
}

void Node::apply_bundle_universe_changes(const Universe&) {}

}
