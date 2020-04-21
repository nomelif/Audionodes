#include "nodes/trigger_sequencer.hpp"

namespace audionodes {

static NodeTypeRegistration<TriggerSequencer> registration("TriggerSequencerNode");

TriggerSequencer::TriggerSequencer() :
    Node(
      {SocketType::trigger},
      {SocketType::trigger},
      []() {
        PropertyTypeList lst {PropertyType::integer};
        for (size_t i = 0; i < max_steps; ++i) {
          lst.push_back(PropertyType::boolean);
        }
        return lst;
      }()
    )
{
  step_count = 1;
  // Step 0 indicates initial state
  ui_current_step = 0;
  send_return_message(0, ui_current_step, false);
}

void TriggerSequencer::receive_binary(int slot, int length, void *_data) {
  if (length > int(max_steps)) length = max_steps;
  if (length < 0) length = 0;
  step_count = length;
  bool *data = static_cast<bool*>(_data);
  for (size_t i = 0; i < step_count; ++i) active[i] = data[i];
  delete [] static_cast<char*>(_data);
}

void TriggerSequencer::process(NodeInputWindow &input) {
  auto &trigger_in = input[0].get<TriggerData>();
  auto &trigger_out = output_window.get_clear<TriggerData>(0);
  if (trigger_in.reset) {
    trigger_out.reset = 1;
    current_step = 0;
  }
  for (auto event : trigger_in.events) {
    current_step++;
    if (current_step > step_count) current_step = 1;
    if (active[current_step-1]) {
      trigger_out.events.push_back(event);
    }
  }
  if (ui_current_step != current_step && !refresh_ui_flag) {
    ui_current_step = current_step;
    send_return_message(0, ui_current_step);
    refresh_ui_flag = true;
  }
}

}
