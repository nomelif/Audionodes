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
    
    operations = [
        ('SUM', ('Add', lambda a, b: a + b)),
        ('SUB', ('Substract', lambda a, b: a - b)),
        ('MUL', ('Multiply', lambda a, b: a * b)),
        ('DIV', ('Divide', lambda a, b: a / b)),
        ('SIN', ('Sine', lambda a, b: np.sin(a))),
        ('COS', ('Cosine', lambda a, b: np.cos(a))),
        ('TAN', ('Tangent', lambda a, b: np.tan(a))),
        ('ASIN', ('Arcsine', lambda a, b: np.arcsin(a))),
        ('ACOS', ('Arccosine', lambda a, b: np.arccos(a))),
        ('ATAN', ('Arctangent', lambda a, b: np.arctan(a))),
        ('POW', ('Power', lambda a, b: a ** b)),
        ('LOG', ('Logarithm', lambda a, b: np.log(a) / np.log(b))),
        ('MIN', ('Minimum', lambda a, b: np.minimum(a, b))),
        ('MAX', ('Maximum', lambda a, b: np.maximum(a, b))),
        ('RND', ('Round', lambda a, b: np.round(a))),
        ('LT', ('Less Than', lambda a, b: (a < b).astype(float))),
        ('GT', ('Greater Than', lambda a, b: (a > b).astype(float))),
        ('MOD', ('Modulo', lambda a, b: a % b)),
        ('ABS', ('Absolute', lambda a, b: np.abs(a))),
    ]
    
    operations_lookup = dict(operations)
    
    def change_operation(self, context):
        self.label = self.operations_lookup[self.opEnum][0]
    
    opEnum = EnumProperty(
        items = [(identifier, name, '', index) for index, (identifier, (name, ev)) in enumerate(operations)],
        update = change_operation
    )

    def callback(self, inputSocketsData, time, rate, length):
        data_1 = self.inputs[0].getData(inputSocketsData)
        data_2 = self.inputs[1].getData(inputSocketsData)
        
        if self.opEnum == 'LOG':
            data_1[0][data_1[0] <= 0] = 1 # log of 1 is zero
            data_2[0][data_2[0] <= 0] = 1 # NaNs this engenders are caught later on
        
        result = self.operations_lookup[self.opEnum][1](data_1[0], data_2[0])
        
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
        self.change_operation(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'opEnum', text='')
        layout.prop(self, 'clamp')
    
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
