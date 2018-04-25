#include "nodes/math.hpp"
#include <cmath>
#include <iostream>

Math::Math() :
    Node({SocketType::audio, SocketType::audio}, {SocketType::audio}, {PropertyType::select})
{}

const Math::MathOperatorList Math::math_operators = {
  // 0: Add
  [](SigT a, SigT b) { return a + b; },
  // 1: Subtract
  [](SigT a, SigT b) { return a - b; },
  // 2: Multiply
  [](SigT a, SigT b) { return a * b; },
  // 3: Divide
  [](SigT a, SigT b) { return a / b; },
  // 4: Sine
  [](SigT a, SigT) { return std::sin(a); },
  // 5: Cosine
  [](SigT a, SigT) { return std::cos(a); },
  // 6: Tangent
  [](SigT a, SigT) { return std::tan(a); },
  // 7: Arcsine
  [](SigT a, SigT) { return std::asin(a); },
  // 8: Arccosine
  [](SigT a, SigT) { return std::acos(a); },
  // 9: Arctangent
  [](SigT a, SigT) { return std::atan(a); },
  // 10: Power
  [](SigT a, SigT b) { return std::pow(a, b); },
  // 11: Logarithm
  [](SigT a, SigT b) { return std::log(a)/std::log(b); },
  // 12: Minimum
  [](SigT a, SigT b) { return std::min(a, b); },
  // 13: Maximum
  [](SigT a, SigT b) { return std::max(a, b);; },
  // 14: Round
  [](SigT a, SigT b) { return std::round(a); },
  // 15: Less than
  [](SigT a, SigT b) { return a < b ? 1.0 : 0.0; },
  // 16: Greater than
  [](SigT a, SigT b) { return a > b ? 1.0 : 0.0; },
  // 17: Modulo
  [](SigT a, SigT b) { return std::fmod(a, b); },
  // 18: Absolute
  [](SigT a, SigT b) { return std::abs(a); }

};

void Math::process(NodeInputWindow &input) {
  size_t n = input.get_channel_amount();
  AudioData::PolyWriter output(output_window[0], n);
  
  const MathOperator &func =
    math_operators[get_property_value(Properties::math_operator)];
  
  for (size_t i = 0; i < n; ++i) {
    const Chunk
      &val1 = input[InputSockets::val1][i],
      &val2 = input[InputSockets::val2][i];
    Chunk &channel = output[i];
    for (size_t j = 0; j < N; ++j) {
      SigT result = func(val1[j], val2[j]);
      channel[j] = std::isfinite(result) ? result : 0.0;
    }
  }
}
