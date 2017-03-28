import bpy
from bpy.types import Node

from bpy.props import EnumProperty, FloatProperty

from .painfuls import fix
pygame, np = fix()

import time

from .node_tree import AudioTreeNode

# This file should always use np.fft.rfft, because we are not dealing with complex numbers
# np.fft.fft is slightly slower to compute

class FIRPass(Node, AudioTreeNode):
    '''A low or high pass FIR filter'''
    bl_idname = 'FIRPassNode'
    bl_label = 'FIR Pass'
    
    
    def callback(self, inputSocketData, time, rate, length):
        N = int(rate*length)
        signal = np.sum(self.inputs[0].getData(inputSocketData)[0], axis=0)
        signal_fft = np.fft.rfft(np.append(signal, np.zeros(N)))
        fr_fft = self.frequency_response[self.path_from_id()]
        result = np.split(np.fft.irfft(signal_fft * fr_fft, N*2), 2)
        
        now_output = result[0] + self.memory[self.path_from_id()]
        self.memory[self.path_from_id()] = result[1]
        
        return ((np.reshape(now_output, (1, N)), self.stamps[self.path_from_id()]), )
        
        
    stamps = {}
    frequency_response = {}
    memory = {}
    
    def init(self, context):
        self.stamps[self.path_from_id()] = [time.time()]
        self.memory[self.path_from_id()] = np.zeros(1024)
        self.outputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")
        self.recalculate_kernel(context)
    
    def recalculate_kernel(self, context):
        # Windowed sinc
        N = 1024 # TODO: get from NodeTree!
        SF = 44100
        
        ktime = (np.arange(N)-N/2)*2/N
        kernel = np.sinc(ktime*self.cutoff/SF*N) * np.blackman(N)
        kernel /= np.sum(kernel)
        
        if self.lohiEnum == 'HIGH':
            # Spectral inversion
            kernel = -kernel
            kernel[N//2] += 1
        frequency_response = np.fft.rfft(np.append(kernel, np.zeros(N)))
        self.frequency_response[self.path_from_id()] = frequency_response
    
    lohiEnum = EnumProperty(
        name = 'Type',
        items = (
            ('LOW', 'Low pass', 'Allow frequencies lower than cutoff'),
            ('HIGH', 'High pass', 'Allow frequencies higher than cutoff'),
        ),
        update = recalculate_kernel
    )
    
    cutoff = FloatProperty(
        name = 'Cutoff frequency',
        update = recalculate_kernel,
        default = 200, min = 0, max = 22050 # Nyqist limit, calculate from sampling fq?
    )
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'lohiEnum', text='')
        layout.prop(self, 'cutoff')
