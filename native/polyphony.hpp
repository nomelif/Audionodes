
#ifndef POLYPHONY_HPP
#define POLYPHONY_HPP

#include "common.hpp"
#include <memory>

class Universe {
  // Describes how the universe changed from the last chunk
  // (which channels were removed and how many new channels were initialized)
  // and uniquely correlates polyphony sources to prevent unwanted mixing
  static int token_counter;
  int unique_token;
  bool variable;
  size_t channel_amount = 0, old_channel_amount = 0, added_channels_amount = 0, removed_channels_amount = 0;
  std::vector<bool> channel_removed;
  
  public:
  typedef std::shared_ptr<Universe> Pointer;
  
  Universe(bool variable = false); // Default constructor
  Universe(bool, size_t); // channel_amount specifying constructor
  
  bool is_polyphonic() const;
  
  bool is_variable() const;
  
  size_t get_channel_amount() const;
  
  bool operator==(const Universe&) const;
  bool operator!=(const Universe&) const;
 
  // Reset if channel_amount isn't the expected value
  void ensure(size_t);
  
  // Removal by lookup-table
  void update(std::vector<bool> removed, size_t added);
  // Removal by indices
  void update(std::vector<size_t> removed, size_t added);
  
  template<class T>
  void apply_delta(std::vector<T> &apply_to) const {
    if (variable) {
      if (old_channel_amount == apply_to.size()) {
        if (removed_channels_amount > 0) {
          // Remove old channels by creating a new vector
          // and re-adding all the channels that were not removed
          std::vector<T> new_vec;
          new_vec.reserve(channel_amount);
          for (size_t i = 0; i < old_channel_amount; ++i) {
            if (!channel_removed[i]) {
              new_vec.push_back(std::move(apply_to[i]));
            }
          }
          apply_to = std::move(new_vec);
        }
        apply_to.reserve(channel_amount);
        // Add new channels
        for (size_t i = 0; i < added_channels_amount; ++i) {
          apply_to.emplace_back();
        }
      } else {
        // Not compatible with previus state of the universe, recreate
        apply_to.clear();
        for (size_t i = 0; i < channel_amount; ++i) {
          apply_to.emplace_back();
        }
      }
    } else {
      // Invariable -- ensure the correct constant amount of channels is present
      if (apply_to.size() != channel_amount) {
        apply_to.clear();
        apply_to.reserve(channel_amount);
        for (size_t i = 0; i < channel_amount; ++i) {
          apply_to.emplace_back();
        }
        apply_to.shrink_to_fit();
      }
    }
  }
  struct Descriptor {
    Pointer input, bundles, output;
    Descriptor(); // All mono
    Descriptor(Pointer, Pointer, Pointer);
    void set_all(Pointer);
  };
};


#endif
