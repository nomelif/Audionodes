
#ifndef COLLAPSE_HPP
#define COLLAPSE_HPP

#include "common.hpp"
#include "node.hpp"

class Collapse : public Node {
  enum InputSockets {
    audio_in
  };
  enum OutputSockets {
    audio_out
  };
  enum Properties {
    flatten_method
  };
  enum FlattenMethods {
    sum, minimum, maximum, product
  };
  public:
  Collapse();
  Universe::Descriptor infer_polyphony_operation(std::vector<Universe::Pointer>);
  void process(NodeInputWindow&);
};

#endif
