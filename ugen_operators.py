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
    
    def callback(self, inputSocketData, timeOffset, rate, length):
        if not self.path_from_id() in self.stamps: # "Init" new node
            self.stamps[self.path_from_id()] = [time.time()]
        return ((np.array([np.random.rand(rate*length)]), np.array(self.stamps[self.path_from_id()])), )
    
    stamps = {}
    
    def init(self, context):
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
        ('SUB', ('Subtract', lambda a, b: a - b)),
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

    def serialize(self):
        base = super(Math, self).serialize()
        base["operation"] = self.opEnum
        base["clamp"] = self.clamp
        return base

    def inflate(self, data):
        self.opEnum = data["operation"]
        self.clamp = data["clamp"]
        super(Math, self).inflate(data)

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

class Flatten(Node, AudioTreeNode):
    '''Flatten multiple audio channels into one'''
    bl_idname = 'FlattenNode'
    bl_label = 'Flatten'
    
    operations = [
        ('SUM', ('Sum', lambda a: a.sum(axis=0))),
        ('MAX', ('Max', lambda a: a.max(axis=0))),
        ('MIN', ('Min', lambda a: a.min(axis=0))),
    ]
    
    operations_lookup = dict(operations)
    
    opEnum = EnumProperty(
        items = [(identifier, name, '', index) for index, (identifier, (name, ev)) in enumerate(operations)]
    )
    
    def callback(self, inputSocketsData, timeOffset, rate, length):
        channels = self.inputs[0].getData(inputSocketsData)[0]
        channel = self.operations_lookup[self.opEnum][1](channels)
        channels = np.expand_dims(channel, axis=0)
        
        if not self.path_from_id() in self.stamps: # "Init" new node
            self.stamps[self.path_from_id()] = [time.time()]
        
        return ((channels, self.stamps), )
    
    stamps = {}
    
    def serialize(self):
        base = super(Flatten, self).serialize()
        base["operation"] = self.opEnum
        return base

    def inflate(self, data):
        self.opEnum = data["operation"]
        super(Flatten, self).inflate(data)
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Multi-channel audio")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'opEnum', text='')

class Sink(Node, AudioTreeNode):
    '''An audio sink'''
    bl_idname = 'AudioSinkNode'
    bl_label = 'Sink'
    # Icon identifier
    bl_icon = 'SOUND'
    
    is_output = True
    is_sink = True
    
    def callback(self, inputSocketsData, timeData, rate, length):
        return self.inputs[0].getData(inputSocketsData)[0].sum(axis=0)
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Audio")
    
    def draw_buttons(self, context, layout):
        if not self.getTree().recording[0]:
            layout.operator('audionodes.record', icon='REC',  text='Record')
        else:
            layout.operator('audionodes.record', icon='PAUSE', text='Stop')
    
