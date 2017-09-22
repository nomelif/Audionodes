
import time

import bpy

from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat
from threading import Lock
import numpy as np
import alsaaudio
from collections import deque
from threading import Thread
from os.path import expanduser
import os
import wave, struct, tempfile
import time
import uuid

# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class AudioTree(NodeTree):
    
    '''Node tree for audio mixer'''
    
    bl_idname = 'AudioTreeType'
    bl_label = 'Audio nodes'
    bl_icon = 'PLAY_AUDIO'

    sample_rate = 44100
    chunk_size = 1024
       
# Custom socket type
class RawAudioSocket(NodeSocket):

    # Description string
    '''Socket for raw audio'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'RawAudioSocketType'
    # Label for nice name display
    bl_label = 'Raw Audio'

    value_prop = bpy.props.FloatProperty()

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "value_prop", text=text)

    def getTree(self):
        return self.id_data

    # Socket color
    def draw_color(self, context, node):
        return (0.607, 0.153, 0.702, 1.0)


# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
