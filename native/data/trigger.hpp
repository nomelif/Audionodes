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
  
  // Iteration helper (when sequentially iterating through 0..N)
  struct Iterator {
    EventSeries::const_iterator it, end;
    inline size_t count(size_t i) {
      size_t amt = 0;
      while (it != end && *it <= i) {
        amt++;
        it++;
      }
      return amt;
    }
  };
  
  Iterator iterate() const;
  
  // Cleanup before write
  void clear();
  
  static TriggerData dummy;
};

}

#endif
