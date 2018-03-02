#include "nodes/sink.hpp"

Sink::Sink() : Node({SocketType::audio}, {}, {}, true) {}

void Sink::process(NodeInputWindow &input) {}

