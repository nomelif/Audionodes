#include "trigger.hpp"

TriggerData::TriggerData(EventSeries events) :
    events(events)
{}
TriggerData::TriggerData() {}

TriggerData TriggerData::dummy = TriggerData();
