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
import numpy as np
import time
from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat

from struct import pack
from array import array

import threading

import wave
import struct
import tempfile
import pygame
import aud
 

if "bpy" in locals():
    if 'node_tree' in locals():

        print('audio_nodes: detected reload event.')
        import importlib

        try:
            modules = (node_tree, piano_capture, oscillators)
            for m in modules:
                importlib.reload(m)
            print("audio_nodes: reloaded modules, all systems operational")

        except Exception as E:
            print('reload failed with error:')
            print(E)


import bpy

from . import node_tree, piano_capture, oscillators

from .node_tree import AudioTreeNode
        
    
class Noise(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''A white noise generator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'NoiseGeneratorNode'
    # Label for nice name display
    bl_label = 'Noise'
    
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, socket, time, rate, length):
        return (np.array([np.random.rand(rate*length)]), np.array(self.stamps[self.path_from_id()]))
    
    stamps = {}
    
    def init(self, context):
        self.stamps[self.path_from_id()] = time.time()
        self.outputs.new('RawAudioSocketType', "Audio")

# Derived from the Node base type.
class Sum(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''The sum of two signals'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SignalSumNode'
    # Label for nice name display
    bl_label = 'Sum'
        
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, socket, time, rate, length):
        data_1 = self.inputs[0].getData(time, rate, length)
        data_2 = self.inputs[1].getData(time, rate, length)
        
        return (data_1[0] + data_2[0], data_1[1])
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

# Derived from the Node base type.
class Mul(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''Multiply two signals'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SignalMulNode'
    # Label for nice name display
    bl_label = 'Mul'
    
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, socketId, time, rate, length):
        data_1 = self.inputs[0].getData(time, rate, length)
        data_2 = self.inputs[1].getData(time, rate, length)
        
        return (data_1[0] * data_2[0], data_1[1])
    
    def init(self, context):
        
        self.outputs.new('RawAudioSocketType', "Audio")
        
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

class Max(Node, AudioTreeNode):
    '''Maximum of two signals'''
    bl_idname = 'SignalMaxNode'
    bl_label = 'Max'
    
    def callback(self, socketId, time, rate, length):
        data_1 = self.inputs[0].getData(time, rate, length)
        data_2 = self.inputs[1].getData(time, rate, length)
        return (np.maximum(data_1[0], data_2[0]), data_1[1])
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

class Min(Node, AudioTreeNode):
    '''Minimum of two signals'''
    bl_idname = 'SignalMinNode'
    bl_label = 'Min'
    
    def callback(self, socketId, time, rate, length):
        data_1 = self.inputs[0].getData(time, rate, length)
        data_2 = self.inputs[1].getData(time, rate, length)
        return (np.minimum(data_1[0], data_2[0]), data_1[1])
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

# Derived from the Node base type.
class Sink(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''An audio sink'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'AudioSinkNode'
    # Label for nice name display
    bl_label = 'Sink'
    # Icon identifier
    bl_icon = 'SOUND'
    
    internalTime = time.time()
    
    running = [True]
    
    def updateSound(self):
        if self.running[0]:
            try:
                self.getTree().play_chunk(self.inputs[0].getData(self.internalTime, 41000, 1024/41000)[0].sum(axis=0))
            except IndexError:
                pass
    t1 = None

    def updateLoop(self):

        while self.running[0]:
            if self.getTree().needsAudio():
                self.internalTime = self.internalTime + 1024/41000
                self.updateSound()
            time.sleep(0.01)
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Audio")
        self.running[0] = True
        self.t1 = threading.Thread(target=self.updateLoop)
        self.t1.start()
    
    # Free function to clean up on removal.
    def free(self):
        self.running[0] = False




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
    ]),
    AudioNodeCategory("AUDIO_OUT", "Outputs", items=[
        NodeItem("AudioSinkNode"),
    ]),
    AudioNodeCategory("AUDIO_OPERATORS", "Operators", items=[
        NodeItem("SignalSumNode"),
        NodeItem("SignalMulNode"),
        NodeItem("SignalMaxNode"),
        NodeItem("SignalMinNode"),
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
