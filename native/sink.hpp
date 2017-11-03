
#ifndef SINK_HPP
#define SINK_HPP

#include "common.hpp"
#include "node.hpp"

class Sink : public Node {
  public:
  const static int type_id = 1;
  Sink();
  std::vector<Chunk> process(std::vector<Chunk>);
};

#endif
