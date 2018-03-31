
#ifndef CIRCULAR_ARRAY_TPP
#define CIRCULAR_ARRAY_TPP

template<typename T, size_t capacity>
void CircularArray<T, capacity>::push_back(T element) {
  if (full()) {
    pop_front();
  }
  buffer[write_index] = element;
  write_index++;
  if (write_index == capacity+1) write_index = 0;
}

template<typename T, size_t capacity>
T CircularArray<T, capacity>::pop_front() {
  T element = buffer[read_index];
  read_index++;
  if (read_index == capacity+1) read_index = 0;
  return element;
}

template<typename T, size_t capacity>
bool CircularArray<T, capacity>::empty() {
  return size() == 0;
}

template<typename T, size_t capacity>
bool CircularArray<T, capacity>::full() {
  return size() == capacity;
}

template<typename T, size_t capacity>
size_t CircularArray<T, capacity>::size() {
  if (write_index >= read_index) {
    return write_index-read_index;
  } else {
    return write_index+(capacity+1-read_index);
  }
}

template<typename T, size_t capacity>
T CircularArray<T, capacity>::back(size_t idx) {
  idx++;
  size_t t = write_index;
  if (t < idx) t += capacity+1;
  return buffer[t-idx];
}

template<typename T, size_t capacity>
T CircularArray<T, capacity>::front(size_t idx) {
  size_t t = read_index;
  t += idx;
  if (t >= capacity+1) t -= capacity+1;
  return buffer[t];
}

template<typename T, size_t capacity>
void CircularArray<T, capacity>::clear() {
  read_index = 0;
  write_index = 0;
}

#endif
