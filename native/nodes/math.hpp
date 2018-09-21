
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
  enum class Operations {
    Add = 0, Subtract, Multiply, Divide,
    Sine, Cosine, Tangent,
    Arcsine, Arccosine, Arctangent,
    Power, Logarithm,
    Minimum, Maximum,
    Round, Less, Greater,
    Modulo, Absolute
  };
  static void compute(Operations, const Chunk&, const Chunk&, Chunk&);

  public:
  Math();
  void process(NodeInputWindow&) override;
};

}

#endif
