# Blender addon sorcery

bl_info = {
    "name": "Audionodes",
    "description": "Create complex soundscapes in real time using nodes.",
    "author": "Roope Salmi, Théo Friberg",
    "version": (0,3,1),
    "blender": (2,77,0),
    "location": "Node Editor > Sound Icon > Add new",
    "warning": "Very much alpha, may blow up in your face.",
    "category": "Node",
    "tracker_url": "https://github.com/nomelif/Audionodes/issues",
    "wiki_url": "https://github.com/nomelif/Audionodes/wiki"
}

# Move all of this into blender/__init__.py?


import bpy
import time
from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat

from struct import pack
from array import array

import threading

import wave
import struct
import tempfile
import platform

from . import blender
node_tree = blender.node_tree
ffi = blender.ffi

### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
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

def register():
    blender.register()
    nodeitems_utils.register_node_categories("AUDIONODES", node_categories)
    ffi.initialize()

def unregister():
    ffi.cleanup()
    nodeitems_utils.unregister_node_categories("AUDIONODES")
    blender.unregister()

import atexit
def exit_handler():
    ffi.cleanup()
atexit.register(exit_handler)

from bpy.app.handlers import persistent
@persistent
def pre_load_handler(_):
    ffi.flag_loading_file = True
    ffi.cleanup()

@persistent
def post_load_handler(_):
    ffi.initialize()
    ffi.flag_loading_file = False
    for tree in bpy.data.node_groups:
        if type(tree) == node_tree.AudioTree:
            tree.post_load_handler()

bpy.app.handlers.load_pre.append(pre_load_handler)
bpy.app.handlers.load_post.append(post_load_handler)

if __name__ == "__main__":
    register()
