
#ifndef CIRCULAR_ARRAY_HPP
#define CIRCULAR_ARRAY_HPP

// Single threaded and random access version of CircularBuffer
// Pops from front if full
template<typename T, size_t capacity>
class CircularArray {
  T buffer[capacity+1];
  size_t write_index=0, read_index=0;
  public:
  void push_back(T);
  T pop_front();
  size_t size();
  bool empty();
  bool full();
  void clear();
  T back(size_t idx=0);
  T front(size_t idx=0);
};

#include "circular_array.tpp"

#endif
