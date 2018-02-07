
#ifndef MATH_HPP
#define MATH_HPP

#include "common.hpp"
#include "node.hpp"
#include <functional>

class Math : public Node {
  enum InputSockets {
    val1, val2
  };
  enum Properties {
    math_operator
  };

  typedef std::function<SigT(SigT, SigT)> MathOperator;
  typedef std::vector<MathOperator> MathOperatorList;
  const static MathOperatorList math_operators;
  public:
  Math();
  NodeOutputWindow process(NodeInputWindow&);
};

#endif
