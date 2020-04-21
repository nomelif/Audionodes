from . import ffi

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class AudioNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'AudioTreeType'

node_categories = [
    AudioNodeCategory("AUDIO_OUT", "Audio output", items=[
        NodeItem("SinkNode"),
    ]),
    AudioNodeCategory("AUDIO_IN", "Audio input", items=[
        NodeItem("MicrophoneNode"),
    ]),
    AudioNodeCategory("GENERATORS", "Generators", items=[
        NodeItem("OscillatorNode"),
        NodeItem("NoiseNode"),
        NodeItem("SamplerNode"),
        NodeItem("ClockNode"),
        NodeItem("TriggerEnvelopeNode"),
    ]),
    AudioNodeCategory("OPERATORS", "Operators", items=[
        NodeItem("MathNode"),
        NodeItem("CollapseNode"),
        NodeItem("ToggleNode")
    ]),
    AudioNodeCategory("FILTERS", "Filters", items=[
        NodeItem("IIRFilterNode"),
    ]),
    AudioNodeCategory("EFFECTS", "Effects", items=[
        NodeItem("DelayNode"),
        NodeItem("RandomAccessDelayNode"),
    ]),
    AudioNodeCategory("MIDI", "MIDI", items=[
        NodeItem("MidiInNode"),
        NodeItem("PianoNode"),
        NodeItem("PitchBendNode"),
        NodeItem("MIDIControlNode"),
        NodeItem("MidiTriggerNode"),
    ]),
]

classes = []

from . import node_tree, nodes, midi_in
for mod in (node_tree, nodes, midi_in):
    classes += mod.classes

import bpy
from bpy.utils import register_class, unregister_class
from bpy.app import timers
def handle_messages():
    for msg in ffi.fetch_messages():
        if msg[0] != -1:
            node_tree.AudioTreeNode.deliver_message(msg)
        else:
            if msg[1] == 0:
                # TODO: Error message from backend
                pass
    return 0.1

def register():
    for cls in classes:
        register_class(cls)
    nodeitems_utils.register_node_categories("AUDIONODES", node_categories)
    timers.register(handle_messages, first_interval=0.1, persistent=True)

def unregister():
    timers.unregister(handle_messages)
    nodeitems_utils.unregister_node_categories("AUDIONODES")
    for cls in reversed(classes):
        unregister_class(cls)
