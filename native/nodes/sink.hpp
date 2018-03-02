
#ifndef SINK_HPP
#define SINK_HPP

#include "common.hpp"
#include "node.hpp"

class Sink : public Node {
  public:
  Sink();
  void process(NodeInputWindow&);
};

#endif
