# Blender addon sorcery

bl_info = {
    "name": "Audionodes",
    "description": "Create complex soundscapes in real time using nodes.",
    "author": "Roope Salmi, Théo Friberg",
    "version": (0,1),
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
            modules = (node_tree, piano_capture, oscillators, ugen_operators, effects)
            for m in modules:
                importlib.reload(m)
            print("audio_nodes: reloaded modules, all systems operational")

        except Exception as E:
            print('reload failed with error:')
            print(E)


import bpy

from . import node_tree, piano_capture, oscillators, ugen_operators, effects


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

# all categories in a list
node_categories = [
    # identifier, label, items list
    AudioNodeCategory("AUDIO_IN", "Inputs", items=[
        NodeItem("SineOscillatorNode"),
        NodeItem("SawOscillatorNode"),
        NodeItem("SquareOscillatorNode"),
        NodeItem("TriangleOscillatorNode"),
        NodeItem("NoiseGeneratorNode"),
        NodeItem("PianoNode"),
        NodeItem("MicNode"),
    ]),
    AudioNodeCategory("AUDIO_OUT", "Outputs", items=[
        NodeItem("AudioSinkNode"),
    ]),
    AudioNodeCategory("AUDIO_OPERATORS", "Operators", items=[
        NodeItem("SignalSumNode"),
        NodeItem("SignalMulNode"),
        NodeItem("SignalMaxNode"),
        NodeItem("SignalMinNode"),
        NodeItem("SignalLogicNode"),
    ]),
    AudioNodeCategory("AUDIO_EFFECTS", "Effects", items=[
        NodeItem("DelayNode"),
    ]),
]


def register():

    try:
        unregister()
    except:
        pass

    bpy.utils.register_module(__name__)
    nodeitems_utils.register_node_categories("AUDIONODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("AUDIONODES")
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
