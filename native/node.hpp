
#ifndef NODE_HPP
#define NODE_HPP

#include "common.hpp"
#include "polyphony.hpp"
#include "data/windows.hpp"
#include <mutex>
#include <functional>
#include <map>

namespace audionodes {


class Node {
  protected:
  bool is_sink;
  
  public:
  enum class SocketType {
    audio, midi, trigger
  };
  enum class PropertyType {
    number, integer, boolean, select
  };
  typedef std::vector<SocketType> SocketTypeList;
  typedef std::vector<PropertyType> PropertyTypeList;
  protected:
  SocketTypeList _input_socket_types, _output_socket_types;
  PropertyTypeList _property_types;
  public:
  // Public const references to type lists
  const SocketTypeList &input_socket_types, &output_socket_types;
  const PropertyTypeList &property_types;
  
  virtual Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  
  // Override if the node has to manage bundles
  virtual void apply_bundle_universe_changes(const Universe&);
  
  bool mark_deletion = false, mark_connected = false, _tmp_connected = false;
  
  bool get_is_sink();
  size_t get_input_count();
  
  void set_input_value(int, SigT);
  SigT get_input_value(int);
  void set_property_value(int, int);
  int get_property_value(int);
  virtual void receive_binary(int, int, void*);
  std::vector<SigT> input_values;
  std::vector<SigT> old_input_values;
  std::vector<int> property_values;
  
  // Called right before the node becomes active in a tree
  virtual void connect_callback();
  // Called after the node has become inactive (process no longer called)
  virtual void disconnect_callback();
  
  void copy_input_values(const Node&);
  NodeOutputWindow output_window;
  virtual void process(NodeInputWindow&) = 0;
  Node(SocketTypeList, SocketTypeList, PropertyTypeList, bool is_sink=false);
  virtual ~Node() = 0;
  
  typedef Node* (*Creator)();
};

// Node registration singleton helper (or factory, if you will)
// Usage:
// static NodeTypeRegistration<NodeClass> registration("identifier");
extern "C" {
  void audionodes_register_node_type(const char*, Node::Creator);
  void audionodes_unregister_node_type(const char*);
}
template<class type>
class NodeTypeRegistration {
  const char *identifier;
  static Node* create_node() {
    return static_cast<Node*>(new type());
  }
  public:
  NodeTypeRegistration(const char *identifier) : identifier(identifier) {
    audionodes_register_node_type(identifier, create_node);
  }
  ~NodeTypeRegistration() {
    audionodes_unregister_node_type(identifier);
  }
};

}

#endif
