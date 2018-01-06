#include "sink.hpp"

Sink::Sink() : Node({SocketType::audio}, {}, {}, true) {}

NodeOutputWindow Sink::process(NodeInputWindow &input) {
  return NodeOutputWindow({});
}

