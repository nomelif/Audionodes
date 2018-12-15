
#ifndef COMMON_HPP
#define COMMON_HPP

#include <vector>
#include <array>
#include <cmath>
#include <algorithm>
#include <cstdint>

namespace audionodes {

#ifdef __linux__
const size_t N = 256;
#else
const size_t N = 512;
#endif

const int RATE = 44100;

#ifndef M_PI
const double M_PI = 3.14159265358979323846;
#endif

typedef float SigT;
typedef std::array<SigT, N> Chunk;
typedef int node_uid;

}

#endif
