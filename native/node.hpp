
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
  void set_property_value(int, int);
  int get_property_value(int);
  virtual void receive_binary(int, int, void*);
  
  struct ConfigurationDescriptor {
    std::string name;
    std::string current_value;
    std::vector<std::string> available_values;
  };
  typedef std::vector<ConfigurationDescriptor> ConfigurationDescriptorList;
  virtual ConfigurationDescriptorList get_configuration_options();
  virtual int set_configuration_option(std::string, std::string);
  
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
  
  private:
  void prepare_output_window();
  
  public:
  Node(SocketTypeList, SocketTypeList, PropertyTypeList, bool is_sink=false);
  Node(Node&);
  virtual ~Node() = 0;
  
  struct Creator {
    Node* (*construct)();
    Node* (*copy)(Node*);
  };
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
  static Node* copy_node(Node *other) {
    type *other_casted = dynamic_cast<type*>(other);
    if (!other_casted) return nullptr;
    return static_cast<Node*>(new type(*other_casted));
  }
  public:
  NodeTypeRegistration(const char *identifier) : identifier(identifier) {
    audionodes_register_node_type(identifier, {create_node, copy_node});
  }
  ~NodeTypeRegistration() {
    audionodes_unregister_node_type(identifier);
  }
};

}

#endif
