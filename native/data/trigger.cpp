#include "trigger.hpp"

namespace audionodes {

TriggerData::TriggerData(EventSeries events) :
    events(events),
    reset(false)
{}
TriggerData::TriggerData() {}

TriggerData::Iterator TriggerData::iterate() const {
  return {events.begin(), events.end()};
}

void TriggerData::clear() {
  events.clear();
  reset = false;
}

TriggerData TriggerData::dummy = TriggerData();

}
