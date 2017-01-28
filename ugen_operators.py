import bpy
from bpy.types import NodeTree, Node # , NodeSocket, NodeSocketFloat

from .painfuls import fix

pygame, np = fix()

import time

import threading

from .node_tree import AudioTreeNode

class Noise(Node, AudioTreeNode):
    '''A white noise generator'''
    bl_idname = 'NoiseGeneratorNode'
    bl_label = 'Noise'
    
    def callback(self, inputSocketData, time, rate, length):
        return ((np.array([np.random.rand(rate*length)]), np.array(self.stamps[self.path_from_id()])), )
    
    stamps = {}
    
    def init(self, context):
        self.stamps[self.path_from_id()] = time.time()
        self.outputs.new('RawAudioSocketType', "Audio")

class Sum(Node, AudioTreeNode):
    '''The sum of two signals'''
    bl_idname = 'SignalSumNode'
    bl_label = 'Sum'
        
    def callback(self, inputSocketsData, time, rate, length):
        data_1 = self.inputs[0].getData(inputSocketsData)
        data_2 = self.inputs[1].getData(inputSocketsData)
        
        return ((data_1[0] + data_2[0], data_1[1]), )
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

class Mul(Node, AudioTreeNode):
    '''Multiply two signals'''
    bl_idname = 'SignalMulNode'
    bl_label = 'Mul'
    
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, inputSocketsData, time, rate, length):
        data_1 = self.inputs[0].getData(inputSocketsData)
        data_2 = self.inputs[1].getData(inputSocketsData)
        
        return ((data_1[0] * data_2[0], data_1[1]), )
    
    def init(self, context):
        
        self.outputs.new('RawAudioSocketType', "Audio")
        
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

class Max(Node, AudioTreeNode):
    '''Maximum of two signals'''
    bl_idname = 'SignalMaxNode'
    bl_label = 'Max'
    
    def callback(self, inputSocketsData, time, rate, length):
        data_1 = self.inputs[0].getData(inputSocketsData)
        data_2 = self.inputs[1].getData(inputSocketsData)
        return ((np.maximum(data_1[0], data_2[0]), data_1[1]), )
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

class Min(Node, AudioTreeNode):
    '''Minimum of two signals'''
    bl_idname = 'SignalMinNode'
    bl_label = 'Min'
    
    def callback(self, inputSocketsData, time, rate, length):
        data_1 = self.inputs[0].getData(inputSocketsData)
        data_2 = self.inputs[1].getData(inputSocketsData)
        return ((np.minimum(data_1[0], data_2[0]), data_1[1]), )
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

class Logic(Node, AudioTreeNode):
    '''Output A or B depending on a condition signal'''
    bl_idname = 'SignalLogicNode'
    bl_label = 'Logic'
    
    def callback(self, inputSocketsData, time, rate, length):
        data_condition = self.inputs[0].getData(inputSocketsData)
        condition = data_condition[0] > 0
        data_a = self.inputs[1].getData(inputSocketsData)
        data_b = self.inputs[2].getData(inputSocketsData)
        result = condition * data_a[0] + (1-condition) * data_b[0]
        return ((result, data_condition[1]), )
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Condition")
        self.inputs.new('RawAudioSocketType', "C > 0")
        self.inputs.new('RawAudioSocketType', "C <= 0")

class Sink(Node, AudioTreeNode):
    '''An audio sink'''
    bl_idname = 'AudioSinkNode'
    bl_label = 'Sink'
    # Icon identifier
    bl_icon = 'SOUND'
    
    is_output = True
    
    running = [True]
    
    def callback(self, inputSocketsData, timeData, rate, length):
        self.getTree().play_chunk(self.inputs[0].getData(inputSocketsData)[0].sum(axis=0))
    
    def updateSound(self, internalTime, order):
        if self.running[0]:
            self.getTree().evaluate_graph(internalTime, order)
    t1 = None
    
    def updateLoop(self):
        internalTime = time.time()
        order = []
        while self.running[0]:
            needsUpdate = False
            
            self.getTree().setupPygame()
            try:
                needsUpdate = self.getTree().needsAudio()
            except AttributeError: # A random error sometimes gets thrown here
                pass
            
            if self.getTree().needsReconstruct():
                self.getTree().reconstruct(order)
            
            if needsUpdate:
                internalTime = internalTime + self.getTree().chunk_size/self.getTree().sample_rate
                self.updateSound(internalTime, order)
            
            time.sleep(0.01)
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Audio")
        self.running[0] = True
        self.t1 = threading.Thread(target=self.updateLoop)
        self.t1.start()
    
    # Free function to clean up on removal.
    def free(self):
        self.running[0] = False
