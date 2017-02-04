import bpy
from bpy.types import NodeTree, Node # , NodeSocket, NodeSocketFloat

from bpy.props import EnumProperty, BoolProperty

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

class Math(Node, AudioTreeNode):
    '''A general math node'''
    bl_idname = 'MathNode'
    bl_label = 'Math'

    clamp = BoolProperty(
    
        name = "Clamp",
        description = "Limit output range to 0..1"

    )

    opEnum = EnumProperty(
    
    items = [('SUM', 'Add', '', 1),
             ('SUB', 'Substract', '', 2),
	     ('MUL', 'Multiply', '', 3),
	     ('DIV', 'Divide', '', 4),
	     ('SIN', 'Sine', '', 5),
	     ('COS', 'Cosine', '', 6),
	     ('TAN', 'Tangent', '', 7),
	     ('ASIN', 'Arcsine', '', 8),
	     ('ACOS', 'Arccosine', '', 9),
	     ('ATAN', 'Arctangent', '', 10),
	     ('POW', 'Power', '', 11),
	     ('LOG', 'Logarithm', '', 12),
	     ('MIN', 'Minimum', '', 13),
	     ('MAX', 'Maximum', '', 14),
	     ('RND', 'Round', '', 15),
	     ('LT', 'Less Than', '', 16),
	     ('GT', 'Greater Than', '', 17),
	     ('MOD', 'Modulo', '', 18),
	     ('ABS', 'Absolute', '', 19)
    ]
    
    )

    def callback(self, inputSocketsData, time, rate, length):
        data_1 = self.inputs[0].getData(inputSocketsData)
        data_2 = self.inputs[1].getData(inputSocketsData)

        result = None

        if self.opEnum == 'SUM':
            result = data_1[0] + data_2[0]
        elif self.opEnum == 'SUB':
            result = data_1[0] - data_2[0]
        elif self.opEnum == 'MUL':
            result = data_1[0] * data_2[0]
        elif self.opEnum == 'DIV':
            result = data_1[0] / data_2[0]
        elif self.opEnum == 'SIN':
            result = np.sin(data_1[0])
        elif self.opEnum == 'COS':
            result = np.cos(data_1[0])
        elif self.opEnum == 'TAN':
            result = np.tan(data_1[0])
        elif self.opEnum == 'ASIN':
            result = np.arcsin(data_1[0])
        elif self.opEnum == 'ACOS':
            result = np.arccos(data_1[0])
        elif self.opEnum == 'ATAN':
            result = np.arctan(data_1[0])
        elif self.opEnum == 'POW':
            result = data_1[0] ** data_2[0]
        elif self.opEnum == 'LOG':

            data_1[0][data_1[0] <= 0] = 1 # log2 of 1 is zero
            data_2[0][data_2[0] <= 0] = 1 # NaNs this engenders are caught later on

            result = np.log2(data_1[0]) / np.log2(data_2[0])
        elif self.opEnum == 'MIN':
            result = np.minimum(data_1[0], data_2[0])
        elif self.opEnum == 'MAX':
            result = np.maximum(data_1[0], data_2[0])
        elif self.opEnum == 'RND':
            result = np.round(data_1[0])
        elif self.opEnum == 'LT':
            result = np.zeros(len(data_1[0]))
            result[np.where(data_1[0] < data_2[0])] = 1.0
        elif self.opEnum == 'GT':
            result = np.zeros(len(data_1[0]))
            result[np.where(data_1[0] > data_2[0])] = 1.0
        elif self.opEnum == 'MOD':
            result = data_1[0] % data_2[0]
        elif self.opEnum == 'ABS':
            result = np.abs(data_1[0])

        # Fix infinite and nan values

        result[np.logical_not(np.isfinite(result))] = 0

        if self.clamp:
            result = np.clip(result, 0, 1)

        stamps = data_1[1] if len(data_1[1]) >= len(data_2[1]) else data_2[1]
        return ((result, stamps),)

    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Result")
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

    def draw_buttons(self, context, layout):

        layout.prop(self, 'clamp')
        layout.prop(self, 'opEnum', text='')

class Mul(Node, AudioTreeNode):
    '''Multiply two signals'''
    bl_idname = 'SignalMulNode'
    bl_label = 'Mul'
    
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, inputSocketsData, time, rate, length):
        data_1 = self.inputs[0].getData(inputSocketsData)
        data_2 = self.inputs[1].getData(inputSocketsData)
        
        stamps = data_1[1] if len(data_1[1]) >= len(data_2[1]) else data_2[1]
        return ((data_1[0] * data_2[0], stamps), )
    
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
        
        stamps = data_1[1] if len(data_1[1]) >= len(data_2[1]) else data_2[1]
        return ((np.maximum(data_1[0], data_2[0]), stamps), )
    
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
        
        stamps = data_1[1] if len(data_1[1]) >= len(data_2[1]) else data_2[1]
        return ((np.minimum(data_1[0], data_2[0]), stamps), )
    
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
        
        if len(data_condition[1]) >= len(data_a[1]) and len(data_condition[1]) >= len(data_b[1]):
            stamps = data_condition[1]
        elif len(data_a[1]) >= len(data_b[1]):
            stamps = data_a[1]
        else:
            stamps = data_b[1]
        return ((result, stamps), )
    
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
