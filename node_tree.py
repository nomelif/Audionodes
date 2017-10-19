
import time

import bpy

from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat
from threading import Lock
import numpy as np
from collections import deque
from threading import Thread
from os.path import expanduser
import os
import wave, struct, tempfile
import time
import uuid

from . import ffi

class AudioTree(NodeTree):
    
    '''Node tree for audio mixer'''
    
    bl_idname = 'AudioTreeType'
    bl_label = 'Audio nodes'
    bl_icon = 'PLAY_AUDIO'

    def init(self):
        pass
    
    def update(self):
        links = ffi.native.begin_tree_update()
        for link in self.links:
            ffi.native.add_tree_update_link(links, link.from_node.get_uid(), link.to_node.get_uid(), link.from_socket.get_index(), link.to_socket.get_index())
        ffi.native.finish_tree_update(links)
    
    def send_value_update(self, node, index, value):
        ffi.native.update_node_input_value(node.get_uid(), index, value)
       
# Custom socket type
class RawAudioSocket(NodeSocket):
    # Description string
    '''Socket for raw audio'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'RawAudioSocketType'
    # Label for nice name display
    bl_label = 'Raw Audio'

    def update_value(self, context):
       self.get_tree().send_value_update(self.node, self.get_index(), self.value_prop)
    
    value_prop = bpy.props.FloatProperty(update=update_value)

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "value_prop", text=text)

    def get_tree(self):
        return self.id_data
    
    def get_index(self):
        return int(self.path_from_id().split('[')[-1][:-1])

    # Socket color
    def draw_color(self, context, node):
        return (0.607, 0.153, 0.702, 1.0)

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class AudioTreeNode:
    bl_icon = 'SOUND'
    
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AudioTreeType'

    def get_tree(self):
        return self.id_data
    
    def send_create_node(self):
        self["unique_id"] = ffi.native.create_node(self.native_type_id)
    
    def copy(self, node):
        self["unique_id"] = ffi.native.copy_node(node.get_uid(), self.native_type_id)
    
    def get_uid(self):
        return self["unique_id"];
    
    def send_remove_node(self):
        ffi.native.remove_node(self.get_uid())

# Proof-of-concept state, remake and move these to another file ASAP
class SineOscillator(Node, AudioTreeNode):
    bl_idname = 'SineOscillatorNode'
    bl_label = 'Sine'
    native_type_id = 0
    def init(self, context):
        self.send_create_node()
        self.inputs.new('RawAudioSocketType', "Frequency (Hz)")
        self.inputs.new('RawAudioSocketType', "Amplitude")
        self.inputs[1].value_prop = 1.0
        self.inputs.new('RawAudioSocketType', "Offset")
        self.outputs.new('RawAudioSocketType', "Audio")
        
    def free(self):
        self.send_remove_node()

class Sink(Node, AudioTreeNode):
    bl_idname = 'SinkNode'
    bl_label = 'Sink'
    bl_icon = 'SOUND'
    native_type_id = 1
    def init(self, context):
        self.send_create_node()
        self.inputs.new('RawAudioSocketType', "Audio")
    
    def free(self):
        self.send_remove_node()


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
