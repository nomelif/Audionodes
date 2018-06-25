#include "nodes/sink.hpp"

namespace audionodes {

static NodeTypeRegistration<Sink> registration("SinkNode");

Sink::Sink() : Node({SocketType::audio}, {}, {}, true) {}

void Sink::process(NodeInputWindow &input) {}

}
