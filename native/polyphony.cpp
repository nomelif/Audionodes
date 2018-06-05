#include "polyphony.hpp"

namespace audionodes {

int Universe::token_counter = 0;

Universe::Universe(bool variable) :
  variable(variable)
{
  if (variable) {
    channel_amount = 0;
  } else {
    channel_amount = 1;
  }
}

Universe::Universe(bool variable, size_t channels) :
    unique_token(token_counter++),
    variable(variable),
    channel_amount(channels)
{}

bool Universe::is_polyphonic() const {
  return variable || channel_amount != 1;
}

bool Universe::is_variable() const {
  return variable;
}

size_t Universe::get_channel_amount() const {
  return channel_amount;
}

bool Universe::operator==(const Universe &other) const {
  // Different variabilities, can't be the same
  if (is_variable() != other.is_variable()) return false;
  if (is_variable()) {
    return unique_token == other.unique_token;
  } else {
    return get_channel_amount() == other.get_channel_amount();
  }
}
bool Universe::operator!=(const Universe &other) const {
  return !operator==(other);
}

void Universe::ensure(size_t expected) {
  if (channel_amount != expected) {
    old_channel_amount = channel_amount;
    channel_amount = expected;
    added_channels_amount = 0;
    removed_channels_amount = 0;
  }
}

void Universe::update(std::vector<bool> removed, size_t added) {
  channel_removed = removed;
  old_channel_amount = channel_amount;
  added_channels_amount = added;
  channel_amount += added;
  removed_channels_amount = 0;
  if (removed.size()) {
    for (bool r : removed) {
      if (r) removed_channels_amount++;
    }
  }
}

void Universe::update(std::vector<size_t> removed, size_t added) {
  old_channel_amount = channel_amount;
  added_channels_amount = added;
  removed_channels_amount = removed.size();
  if (removed_channels_amount > 0) {
     channel_removed = std::vector<bool>(old_channel_amount, false);
     for (size_t idx : removed) channel_removed[idx] = true;
  }
  channel_amount += added_channels_amount;
  channel_amount -= removed_channels_amount;
}

Universe::Descriptor::Descriptor() {
  Pointer mono(new Universe());
  input = bundles = output = mono;
}

Universe::Descriptor::Descriptor(Pointer input, Pointer bundles, Pointer output) :
    input(input),
    bundles(bundles),
    output(output)
{}

void Universe::Descriptor::set_all(Pointer to) {
  input = bundles = output = to;
}

}
