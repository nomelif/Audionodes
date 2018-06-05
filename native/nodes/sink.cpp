#include "nodes/sink.hpp"

namespace audionodes {

Sink::Sink() : Node({SocketType::audio}, {}, {}, true) {}

void Sink::process(NodeInputWindow &input) {}

}
