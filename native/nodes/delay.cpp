#include "delay.hpp"

namespace audionodes {

Delay::Delay() :
    Node(SocketTypeList(3, SocketType::audio), {SocketType::audio}, {})
{}

void Delay::apply_bundle_universe_changes(const Universe &universe) {
  universe.apply_delta(bundles);
}

void Delay::process(NodeInputWindow &input) {
  size_t n = input.get_channel_amount();
  AudioData::PolyWriter output(output_window[0], n);
  
  for (size_t i = 0; i < n; ++i) {
    const Chunk
      &signal = input[InputSockets::signal][i],
      &delay_time = input[InputSockets::delay_time][i],
      &feedback = input[InputSockets::feedback][i];
    bundles[i].process(signal, delay_time, feedback, output[i]);
  }
}

void Delay::DynamicBuffer::process(
    const Chunk &input, const Chunk &delay_time, const Chunk &feedback,
    Chunk &output) {
  for (size_t i = 0; i < N; ++i) {
    size_t target_size = std::max(SigT(1), std::round(delay_time[i]*RATE));
    bool grow = size <= target_size, shrink = size >= target_size;
    output[i] = 0;
    if (shrink) {
      // Pop from buffer
      output[i] = read_head.block->buf[read_head.pos];
      read_head.pos++;
      size--;
      if (read_head.pos >= Block::length) {
        if (block_amt-block_dist > min_blocks) {
          // enough unused blocks, contract
          // Removing from the write_head's end since we can access
          // the pointers there.
          Block *to_remove = write_head.block->next;
          write_head.block->next = to_remove->next;
          delete to_remove;
          block_amt--;
        }
        read_head.block = read_head.block->next;
        read_head.pos = 0;
        block_dist--;
      }
      if (!std::isfinite(last_output)) last_output = 0;
    }
    if (grow) {
      SigT val = input[i]+last_output*feedback[i];
      
      // Push to buffer
      write_head.block->buf[write_head.pos] = val;
      write_head.pos++;
      size++;
      if (write_head.pos >= Block::length) {
        if (write_head.block->next == read_head.block) {
          // running out of blocks, expand
          Block *new_block = new Block();
          new_block->next = write_head.block->next;
          write_head.block->next = new_block;
          block_amt++;
        }
        write_head.block = write_head.block->next;
        write_head.pos = 0;
        block_dist++;
      }
    }
  }
}

Delay::DynamicBuffer::DynamicBuffer() {
  // Construct initial circular linkage
  Block *first;
  Block **last_ref = &first;
  for (size_t i = 0; i < min_blocks; ++i) {
    Block *current = new Block();
    *last_ref = current;
    last_ref = &current->next;
    block_amt++;
  }
  *last_ref = first;
  read_head = {first, 0};
  write_head = {first, 0};
}

Delay::DynamicBuffer::~DynamicBuffer() {
  Block *start = read_head.block;
  if (start == nullptr) return;
  Block *next = start;
  do {
    Block *current = next;
    next = current->next;
    delete current;
  } while (next != start);
}

Delay::DynamicBuffer& Delay::DynamicBuffer::operator=(DynamicBuffer &&from) {
  read_head = from.read_head;
  write_head = from.write_head;
  size = from.size;
  block_amt = from.block_amt;
  block_dist = from.block_dist;
  last_output = from.last_output;
  from.read_head = {nullptr, 0};
  from.write_head = {nullptr, 0};
  from.size = from.block_amt = from.block_dist = 0;
  return *this;
}

Delay::DynamicBuffer::DynamicBuffer(DynamicBuffer &&from) {
  operator=(std::move(from));
}

}
