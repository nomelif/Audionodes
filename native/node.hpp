
#ifndef NODE_HPP
#define NODE_HPP

#include "common.hpp"
#include "polyphony.hpp"
#include "data_windows.hpp"
#include <mutex>

class Node {
  protected:
  bool is_sink;
  size_t input_count, output_count, property_count;
  std::vector<SigT> input_values;
  std::vector<int> property_values;
  std::mutex input_values_mutex;
  public:
  virtual Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  
  // Override if the node has to manage bundles
  virtual void apply_bundle_universe_changes(const Universe&);
  
  bool mark_deletion;
  std::vector<SigT> old_input_values;
  
  bool get_is_sink();
  size_t get_input_count();
  
  void set_input_value(int, SigT);
  SigT get_input_value(int);
  void set_property_value(int, int);
  int get_property_value(int);
  
  void copy_input_values(Node*);
  virtual NodeOutputWindow process(NodeInputWindow&) = 0;
  Node(size_t, size_t, size_t, bool is_sink=false);
  virtual ~Node() = 0;
};

#endif