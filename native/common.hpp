
#ifndef COMMON_HPP
#define COMMON_HPP

#include <vector>
#include <array>
#define _USE_MATH_DEFINES
#include <cmath>
#include <algorithm>
#include <cstdint>

namespace audionodes {

#ifdef __linux__
constexpr size_t N = 256;
#else
constexpr size_t N = 512;
#endif

constexpr int RATE = 44100;

#ifndef M_PI
constexpr double M_PI = 3.14159265358979323846;
#endif

typedef float SigT;
typedef std::array<SigT, N> Chunk;
typedef int node_uid;

}

#endif
