#ifndef DATA_TRIGGER_HPP
#define DATA_TRIGGER_HPP

#include "common.hpp"
#include "data.hpp"

namespace audionodes {

struct TriggerData : public Data {
  typedef size_t Event;
  typedef std::vector<Event> EventSeries;
  EventSeries events;
  bool reset;
  TriggerData(EventSeries);
  TriggerData();
  
  // Cleanup before write
  void clear();
  
  static TriggerData dummy;
};

}

#endif
