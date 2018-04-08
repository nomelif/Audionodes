# Blender addon sorcery

bl_info = {
    "name": "Audionodes",
    "description": "Create complex soundscapes in real time using nodes.",
    "author": "Roope Salmi, Théo Friberg",
    "version": (1,0),
    "blender": (2,77,0),
    "location": "Node Editor > Sound Icon > Add new",
    "warning": "Very much alpha, may blow up in your face.",
    "category": "Node",
    "tracker_url": "https://github.com/nomelif/Audionodes/issues",
    "wiki_url": "https://github.com/nomelif/Audionodes"
}


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

if "bpy" in locals():
    if 'node_tree' in locals():

        print('audio_nodes: detected reload event.')
        import importlib

        try:
            modules = (node_tree,)
            for m in modules:
                importlib.reload(m)
            print("audio_nodes: reloaded modules, all systems operational")

        except Exception as E:
            print('reload failed with error:')
            print(E)


import bpy

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
    AudioNodeCategory("GENERATORS", "Generators", items=[
        NodeItem("OscillatorNode"),
        NodeItem("NoiseNode"),
    ]),
    AudioNodeCategory("OPERATORS", "Operators", items=[
        NodeItem("MathNode"),
        NodeItem("CollapseNode"),
    ]),
    AudioNodeCategory("FILTERS", "Filters", items=[
        NodeItem("IIRFilterNode"),
    ]),
    AudioNodeCategory("MIDI", "MIDI", items=[
        NodeItem("MidiInNode"),
        NodeItem("PianoNode"),
        NodeItem("PitchBendNode"),
        NodeItem("SliderNode"),
    ]),
]

def register():

    try:
        unregister()
    except:
        pass

    bpy.utils.register_module(__name__)
    nodeitems_utils.register_node_categories("AUDIONODES", node_categories)
    ffi.initialize()

def unregister():
    ffi.cleanup()
    nodeitems_utils.unregister_node_categories("AUDIONODES")
    bpy.utils.unregister_module(__name__)

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
