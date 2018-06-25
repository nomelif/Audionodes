#include "nodes/math.hpp"
#include <cmath>

namespace audionodes {

static NodeTypeRegistration<Math> registration("MathNode");

Math::Math() :
    Node({SocketType::audio, SocketType::audio}, {SocketType::audio}, {PropertyType::select})
{}

void Math::compute(Operations operation, const Chunk &_a, const Chunk &_b, Chunk &out) {
  // Placing the switch inside the loop has worse performance. (as of GCC 7.3.0)
  switch (operation) {
    using O = Operations;
#define X(op) for (size_t i = 0; i < N; ++i) { \
  out[i] = (op); \
} \
break;
#define a _a[i]
#define b _b[i]
    case O::Add:        X( a + b )
    case O::Subtract:   X( a - b )
    case O::Multiply:   X( a * b )
    case O::Divide:     X( a / b )
    case O::Sine:       X( std::sin(a) )
    case O::Cosine:     X( std::cos(a) )
    case O::Tangent:    X( std::tan(a) )
    case O::Arcsine:    X( std::asin(a) )
    case O::Arccosine:  X( std::acos(a) )
    case O::Arctangent: X( std::atan(a) )
    case O::Power:      X( std::pow(a, b) )
    case O::Logarithm:  X( std::log(a) / std::log(b) )
    case O::Minimum:    X( std::min(a, b) )
    case O::Maximum:    X( std::max(a, b) )
    case O::Round:      X( std::round(a) )
    case O::Less:       X( a < b ? 1.0 : 0.0 )
    case O::Greater:    X( a > b ? 1.0 : 0.0 )
    case O::Modulo:     X( std::fmod(a, b) )
    case O::Absolute:   X( std::abs(a) )
#undef X
#undef a
#undef b
  }
  for (size_t i = 0; i < N; ++i) {
    out[i] = std::isfinite(out[i]) ? out[i] : 0.0;
  }
}

void Math::process(NodeInputWindow &input) {
  size_t n = input.get_channel_amount();
  AudioData::PolyWriter output(output_window[0], n);
  
  Operations op = static_cast<Operations>(get_property_value(Properties::math_operator));
  
  for (size_t i = 0; i < n; ++i) {
    const Chunk
      &val1 = input[InputSockets::val1][i],
      &val2 = input[InputSockets::val2][i];
    compute(op, val1, val2, output[i]);
  }
}

}
