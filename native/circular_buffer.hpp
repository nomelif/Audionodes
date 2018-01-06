
#ifndef CIRCULAR_BUFFER_HPP
#define CIRCULAR_BUFFER_HPP

#include <atomic>
#include <iostream>

// Allows separate inserter and consumer thread,
// but not multiple threads for the same operation
template<typename T, size_t size>
class CircularBuffer {
  T buffer[size];
  std::atomic<size_t> write_index, read_index;
  const bool verbose;
  public:
  void push(T);
  // Shall not be called when empty (check it first)
  T pop();
  bool empty();
  bool full();
  // Use with caution: both threads have to agree on the clear synchronously
  void clear();
  CircularBuffer(bool);
};

#include "circular_buffer.tpp"

#endif
