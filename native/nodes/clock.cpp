#include "nodes/clock.hpp"

namespace audionodes {

static NodeTypeRegistration<Clock> registration("ClockNode");

Clock::Clock() :
    Node({SocketType::audio, SocketType::trigger}, {SocketType::trigger}, {})
{}

Universe::Descriptor Clock::infer_polyphony_operation(std::vector<Universe::Pointer>) {
  return Universe::Descriptor();
}

void Clock::process(NodeInputWindow &input) {
  auto &bpm = input[InputSockets::rate][0];
  auto &run_stop = input[InputSockets::run_stop].get<TriggerData>();
  auto &output = output_window.get_clear<TriggerData>(OutputSockets::trigger);
  if (run_stop.reset) {
    output.reset = true;
    running = true;
    time_since_tick = 0;
    tick_now = true;
  }
  auto it = run_stop.iterate();
  for (size_t i = 0; i < N; ++i) {
    running ^= it.count(i) % 2;
    if (running) {
      double interval = 60.*RATE/bpm[i];
      if (time_since_tick > interval) {
        tick_now = true;
        time_since_tick = std::fmod(time_since_tick-interval, 1.);
      }
      time_since_tick++;
    }
    if (tick_now) {
      output.events.push_back(i);
      tick_now = false;
    }
  }
}

}
