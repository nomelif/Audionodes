#include "sink.hpp"

Sink::Sink() : Node(1, 0, 0, true) {}

NodeOutputWindow Sink::process(NodeInputWindow &input) {
  return NodeOutputWindow({});
}

