import bpy
from bpy.types import Node

from bpy.props import EnumProperty, FloatProperty

from .painfuls import fix
pygame, np = fix()

import time

from .node_tree import AudioTreeNode

# This file should always use np.fft.rfft, because we are not dealing with complex numbers
# np.fft.fft is slightly slower to compute
def fftconvolve(a, b, N):
    z = np.zeros(N)
    a = np.fft.rfft(np.append(a, z))
    b = np.fft.rfft(np.append(b, z))
    return np.fft.irfft(a * b, 2*N)

class FIRPass(Node, AudioTreeNode):
    '''A low or high pass FIR filter'''
    bl_idname = 'FIRPassNode'
    bl_label = 'FIR Pass'
    
    
    def callback(self, inputSocketData, time, rate, length):
        pass
        
    stamps = {}
    
    def init(self, context):
        self.stamps[self.path_from_id()] = [time.time()]
        self.outputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")
    
    def recalculate_kernel(self, context):
        pass
    
    lohiEnum = EnumProperty(
        name = 'Type',
        items = (
            ('LOW', 'Low pass', 'Allow frequencies lower than cutoff'),
            ('HIGH', 'High pass', 'Allow frequencies higher than cutoff'),
        ),
        update = recalculate_kernel
    )
    
    cutoffEnum = FloatProperty(
        name = 'Cutoff frequency',
        update = recalculate_kernel,
        default = 200, min = 0, max = 22050 # Nyqist limit, calculate from sampling fq?
    )
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'lohiEnum', text='')
        layout.prop(self, 'cutoffEnum')
