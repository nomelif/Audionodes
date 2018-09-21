
#ifndef NOISE_HPP
#define NOISE_HPP

#include "common.hpp"
#include "node.hpp"
#include <random>

namespace audionodes {

class Noise : public Node {
  std::mt19937 generator;
  std::uniform_real_distribution<> distribution;
  public:
  Noise();
  void process(NodeInputWindow&) override;
};

}

#endif
