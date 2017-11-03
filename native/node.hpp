
#ifndef NODE_HPP
#define NODE_HPP

#include "common.hpp"
#include <mutex>

class Node {
  protected:
  bool is_sink;
  size_t input_count, output_count;
  std::vector<float> input_values;
  std::mutex input_values_mutex;
  public:
  bool mark_deletion;
  std::vector<float> old_input_values;
  
  bool get_is_sink();
  size_t get_input_count();
  void set_input_value(int, float);
  float get_input_value(int);
  void copy_input_values(Node*);
  virtual std::vector<Chunk> process(std::vector<Chunk>) = 0;
  Node(size_t, size_t, bool is_sink=false);
  virtual ~Node();
};

#endif
