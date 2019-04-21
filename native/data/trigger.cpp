#include "trigger.hpp"

namespace audionodes {

TriggerData::TriggerData(EventSeries events) :
    events(events),
    reset(false)
{}
TriggerData::TriggerData() {}

void TriggerData::clear() {
  events.clear();
  reset = false;
}

TriggerData TriggerData::dummy = TriggerData();

}
