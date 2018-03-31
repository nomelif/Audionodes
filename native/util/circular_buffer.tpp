
#ifndef CIRCULAR_BUFFER_TPP
#define CIRCULAR_BUFFER_TPP

template<typename T, size_t capacity>
void CircularBuffer<T, capacity>::push(T element) {
  if (full()) {
    // Can't push
    if (verbose) {
      std::clog << "Audionodes native: CircularBuffer at " << this << " is full but push was attempted" << std::endl;
    }
    return;
  }
  size_t tmp_write_index = write_index.load();
  buffer[tmp_write_index] = element;
  tmp_write_index++;
  if (tmp_write_index == capacity) tmp_write_index = 0;
  write_index = tmp_write_index;
}

template<typename T, size_t capacity>
T CircularBuffer<T, capacity>::pop() {
  size_t tmp_read_index = read_index.load();
  T element = buffer[tmp_read_index];
  tmp_read_index++;
  if (tmp_read_index == capacity) tmp_read_index = 0;
  read_index = tmp_read_index;
  return element;
}

template<typename T, size_t capacity>
bool CircularBuffer<T, capacity>::empty() {
  return write_index.load() == read_index.load();
}

template<typename T, size_t capacity>
bool CircularBuffer<T, capacity>::full() {
  size_t tmp_read_index = read_index.load(), tmp_write_index = write_index.load();
  // The buffer is full if a new write would cause the indices to be same
  return tmp_read_index == tmp_write_index+1
  // Handle case where read index is at 0 seperately
    || (tmp_read_index == 0 && tmp_write_index == capacity-1);
}

template<typename T, size_t capacity>
void CircularBuffer<T, capacity>::clear() {
  read_index = 0;
  write_index = 0;
}

template<typename T, size_t capacity>
CircularBuffer<T, capacity>::CircularBuffer(bool verbose) :
  write_index(0),
  read_index(0),
  verbose(verbose)
{}

#endif
