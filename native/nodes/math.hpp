
#ifndef MATH_HPP
#define MATH_HPP

#include "common.hpp"
#include "node.hpp"
#include <functional>

namespace audionodes {

class Math : public Node {
  enum InputSockets {
    val1, val2
  };
  enum Properties {
    math_operator
  };

  typedef void (*MathOperator)(const Chunk&, const Chunk&, Chunk&);
  const static MathOperator math_operators[];
  public:
  Math();
  void process(NodeInputWindow&);
};

}

#endif
