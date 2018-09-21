
#ifndef DELAY_HPP
#define DELAY_HPP

#include "common.hpp"
#include "node.hpp"

namespace audionodes {

class Delay : public Node {
  enum InputSockets {
    signal, delay_time, feedback
  };
  enum OutputSockets {
    output // only wet
  };
  
  class DynamicBuffer {
    // cyclic linked list of "blocks", a sort of dynamic circular buffer
    static const size_t min_blocks = 4;
    struct Block {
      static const size_t length = 1022;
      SigT buf[length];
      Block *next;
    };
    struct Head {
      Block *block = nullptr;
      size_t pos = 0;
    } read_head, write_head;
    size_t size = 0, block_amt = 0, block_dist = 0;
    void dealloc();
    public:
    void process(const Chunk&, const Chunk&, const Chunk&, Chunk&);
    DynamicBuffer& operator=(DynamicBuffer&&) noexcept;
    DynamicBuffer(DynamicBuffer&&) noexcept;
    DynamicBuffer& operator=(const DynamicBuffer&) = delete;
    DynamicBuffer(const DynamicBuffer&) = delete;
    
    DynamicBuffer();
    ~DynamicBuffer();
  };
  
  std::vector<DynamicBuffer> bundles;
  
  public:
  Delay();
  void apply_bundle_universe_changes(const Universe&) override;
  void process(NodeInputWindow&) override;
};

}

#endif
