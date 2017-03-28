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
        cutoff = np.clip(np.average(self.inputs[0].getData(inputSocketData)[0]), 0, rate/2)
        signal = np.sum(self.inputs[1].getData(inputSocketData)[0], axis=0)
        signal_fft = np.fft.rfft(np.append(signal, np.zeros(N)))
        
        ktime = (np.arange(N)-N/2)*2/N
        kernel = np.sinc(ktime*cutoff/rate*N) * np.blackman(N)
        kernel /= np.sum(kernel)
        
        if self.lohiEnum == 'HIGH':
            # Spectral inversion
            kernel = -kernel
            kernel[N//2] += 1
        frequency_response = np.fft.rfft(np.append(kernel, np.zeros(N)))
        
        result = np.split(np.fft.irfft(signal_fft * frequency_response, N*2), 2)
        
        now_output = result[0] + self.memory[self.path_from_id()]
        self.memory[self.path_from_id()] = result[1]
        
        return ((np.reshape(now_output, (1, N)), self.stamps[self.path_from_id()]), )
        
        
    stamps = {}
    memory = {}
    
    def init(self, context):
        self.stamps[self.path_from_id()] = [time.time()]
        self.memory[self.path_from_id()] = 0
        self.outputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Cutoff (Hz)")
        self.inputs.new('RawAudioSocketType', "Audio")
    
    lohiEnum = EnumProperty(
        name = 'Type',
        items = (
            ('LOW', 'Low pass', 'Allow frequencies lower than cutoff'),
            ('HIGH', 'High pass', 'Allow frequencies higher than cutoff'),
        )
    )
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'lohiEnum', text='')
