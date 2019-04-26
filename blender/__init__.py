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
        NodeItem("SliderNode"),
        NodeItem("MidiTriggerNode"),
    ]),
]

classes = []

from . import node_tree, nodes, midi_in
for mod in (node_tree, nodes, midi_in):
    classes += mod.classes

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    nodeitems_utils.register_node_categories("AUDIONODES", node_categories)

def unregister():
    from bpy.utils import unregister_class
    nodeitems_utils.unregister_node_categories("AUDIONODES")
    for cls in reversed(classes):
        unregister_class(cls)
