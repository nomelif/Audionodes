
#ifndef RANDOM_ACCESS_DELAY
#define RANDOM_ACCESS_DELAY

#include "common.hpp"
#include "node.hpp"
#include <vector>

namespace audionodes {

class RandomAccessDelay : public Node {
  enum InputSockets {
    signal, delay_time, feedback
  };
  enum OutputSockets {
    output // only wet
  };
  enum Properties {
    buffer_size
  };
  struct Bundle {
    std::vector<SigT> buffer;
    size_t write_head = 0;
    void resize(size_t);
  };
  
  std::vector<Bundle> bundles;
  
  public:
  RandomAccessDelay();
  void apply_bundle_universe_changes(const Universe&) override;
  void process(NodeInputWindow&) override;
};

}

#endif
