#include "nodes/math.hpp"

namespace audionodes {

#include <cmath>

Math::Math() :
    Node({SocketType::audio, SocketType::audio}, {SocketType::audio}, {PropertyType::select})
{}

const Math::MathOperator Math::math_operators[] = {
#define X(op) [](const Chunk &_a, const Chunk &_b, Chunk &out) { \
  for (size_t i = 0; i < N; ++i) { \
    out[i] = op; \
    out[i] = std::isfinite(out[i]) ? out[i] : 0.0; \
  } \
}
#define a _a[i]
#define b _b[i]
  // 0: Add
  X( a + b ),
  // 1: Subtract
  X( a - b ),
  // 2: Multiply
  X( a * b ),
  // 3: Divide
  X( a / b ),
  // 4: Sine
  X( std::sin(a) ),
  // 5: Cosine
  X( std::cos(a) ),
  // 6: Tangent
  X( std::tan(a) ),
  // 7: Arcsine
  X( std::asin(a) ),
  // 8: Arccosine
  X( std::acos(a) ),
  // 9: Arctangent
  X( std::atan(a) ),
  // 10: Power
  X( std::pow(a, b) ),
  // 11: Logarithm
  X( std::log(a)/std::log(b) ),
  // 12: Minimum
  X( std::min(a, b) ),
  // 13: Maximum
  X( std::max(a, b) ),
  // 14: Round
  X( std::round(a) ),
  // 15: Less than
  X( a < b ? 1.0 : 0.0 ),
  // 16: Greater than
  X( a > b ? 1.0 : 0.0 ),
  // 17: Modulo
  X( std::fmod(a, b) ),
  // 18: Absolute
  X( std::abs(a) )
#undef X
#undef a
#undef b
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
    func(val1, val2, output[i]);
  }
}

}
