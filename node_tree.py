
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
        ffi.C.push(ffi.queue, 123)
    
       
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



def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
