#include "sink.hpp"

Sink::Sink() : Node(1, 0, 0, true) {}
std::vector<Chunk> Sink::process(std::vector<Chunk> input) {
  return input;
}
