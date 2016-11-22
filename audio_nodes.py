import bpy
import numpy as np
import time
from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat

from struct import pack
from array import array
import pyaudio

import threading
 
"""
Class using Pyaudio for simple playback of raw audio-data represented by a float array.
The user only needs to create an object and call the play_chunk method.
 
"""

class Playback(object):
    '''
    classdocs
    '''
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16
    RATE = 41000
 
    def __init__(self):
        '''
        Constructor
        '''
        self.audioDevice = pyaudio.PyAudio()
        self.stream = self.audioDevice.open(format=Playback.FORMAT,
                                            channels=1,
                                            rate=Playback.RATE,
                                            output=True,
                                            frames_per_buffer=Playback.CHUNK_SIZE)
 
    def play_chunk(self, inputArray):
 
        if self.stream.is_stopped():
            self.stream = self.audioDevice.open(format=Playback.FORMAT,
                                                channels=1,
                                                rate=Playback.RATE,
                                                output=True,
                                                frames_per_buffer=Playback.CHUNK_SIZE)
 
        output = array('h')
 
        for i in range(len(inputArray)):
            # Check for Clips
            if int(inputArray[i]*32768) < -32767:
                output.append(-32767)
                print("clip at "+str(i))
            elif int(inputArray[i]*32768) > 32767:
                output.append(32767)
                print("clip at "+str(i))
            else:
                output.append(int(inputArray[i]*32767))
 
        # Converts to bitstream for output
        output = pack('<' + ('h'*len(output)), *output)
 
        self.stream.write(output)
 
    def stopStream(self):
 
        self.stream.stop_stream()
 
    def __del__(self):
        self.stream.close()
        self.audioDevice.terminate()

# Implementation of custom nodes from Python


# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class AudioTree(NodeTree):
    # Description string
    '''Node tree for audio mixer.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'AudioTreeType'
    # Label for nice name display
    bl_label = 'Audio nodes'
    # Icon identifier
    bl_icon = 'PLAY_AUDIO'


# Custom socket type
class RawAudioSocket(NodeSocket):
    # Description string
    '''Socket for raw audio'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'RawAudioSocketType'
    # Label for nice name display
    bl_label = 'Raw Audio'
    
    value_prop = bpy.props.FloatProperty()
    
        
    def getData(self, time, rate, length):
        if self.is_output:
            return self.node.callback(self, time, rate, length)
        elif self.is_linked:
            return self.links[0].from_socket.getData(time, rate, length)
        else:
            print(self.value_prop)
            return np.array([self.value_prop]*int(length*rate))

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "value_prop", text="")

    
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
    
    def update(self):
        print(self.bl_label)
    
    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")
    
    def draw_buttons(self, context, layout):
        pass

class Sine(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''A sine wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SineOscillatorNode'
    # Label for nice name display
    bl_label = 'Sine'
    
    last_state = {}
    
    def callback(self, socket, time, rate, length):
        if self.inputs[0].is_linked:
            freq = self.inputs[0].getData(time, rate, length)
            last_state = 0
            if self.path_from_id() in self.last_state:
                last_state = self.last_state[self.path_from_id()]
            output = np.cumsum(freq)/rate + last_state
            self.last_state[self.path_from_id()] = output[-1] % 1
            return np.sin(output*np.pi*2)
        else:
            return np.sin((np.arange(rate*length)/rate+time)*np.pi * 2 * self.inputs[0].getData(time, rate, length))
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Frequency (Hz)")
        self.outputs.new('RawAudioSocketType', "Audio")
    
class Saw(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''A saw wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SawOscillatorNode'
    # Label for nice name display
    bl_label = 'Saw'
    
    last_state = {}
    
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, socket, time, rate, length):
        if self.inputs[0].is_linked:
            freq = self.inputs[0].getData(time, rate, length)
            last_state = 0
            if self.path_from_id() in self.last_state:
                last_state = self.last_state[self.path_from_id()]
            output = np.cumsum(freq)/rate + last_state
            self.last_state[self.path_from_id()] = output[-1] % 1
            return output * 2 % 2 - 1
        else:
            return (np.arange(rate*length)/rate+time) * self.inputs[0].getData(time, rate, length) * 2 % 2 - 1
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Frequency (Hz)")
        self.outputs.new('RawAudioSocketType', "Audio")
    
class Square(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''A square wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SquareOscillatorNode'
    # Label for nice name display
    bl_label = 'Square'
    
    last_state = {}
    
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, socket, time, rate, length):
        if self.inputs[0].is_linked:
            freq = self.inputs[0].getData(time, rate, length)
            last_state = 0
            if self.path_from_id() in self.last_state:
                last_state = self.last_state[self.path_from_id()]
            output = np.cumsum(freq)/rate + last_state
            self.last_state[self.path_from_id()] = output[-1] % 1
            return np.greater(output % 1, 0.5) * 2 - 1
        else:
            return np.greater((np.arange(rate*length)/rate+time) * self.inputs[0].getData(time, rate, length) % 1, 0.5) * 2 - 1
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Frequency (Hz)")
        self.outputs.new('RawAudioSocketType', "Audio")

class Triangle(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''A triangle wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'TriangleOscillatorNode'
    # Label for nice name display
    bl_label = 'Triangle'
    
    last_state = {}
    
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, socket, time, rate, length):
        if self.inputs[0].is_linked:
            freq = self.inputs[0].getData(time, rate, length)
            last_state = 0
            if self.path_from_id() in self.last_state:
                last_state = self.last_state[self.path_from_id()]
            output = np.cumsum(freq)/rate + last_state
            self.last_state[self.path_from_id()] = output[-1] % 1
            return np.abs(output * 4 % 4 - 2) - 1
        else:
            return np.abs((np.arange(rate*length)/rate+time) * self.inputs[0].getData(time, rate, length) * 4 % 4 - 2) - 1
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Frequency (Hz)")
        self.outputs.new('RawAudioSocketType', "Audio")
    
class Noise(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''A white noise generator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'NoiseGeneratorNode'
    # Label for nice name display
    bl_label = 'Noise'
    
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, socket, time, rate, length):
        return np.random.rand(rate*length)
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")

# Derived from the Node base type.
class Sum(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''The sum of two signals'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SignalSumNode'
    # Label for nice name display
    bl_label = 'Sum'
        
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, socket, time, rate, length):
        data_1 = self.inputs[0].getData(time, rate, length)
        data_2 = self.inputs[1].getData(time, rate, length)
        
        return data_1 + data_2
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

# Derived from the Node base type.
class Mul(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''Multiply two signals'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SignalMulNode'
    # Label for nice name display
    bl_label = 'Mul'
    
    # This method gets the current time as a parameter as well as the socket input is wanted for.
    def callback(self, socketId, time, rate, length):
        data_1 = self.inputs[0].getData(time, rate, length)
        data_2 = self.inputs[1].getData(time, rate, length)
        
        return data_1 * data_2
    
    def init(self, context):
        
        self.outputs.new('RawAudioSocketType', "Audio")
        
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

# Derived from the Node base type.
class Sink(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''An audio sink'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'AudioSinkNode'
    # Label for nice name display
    bl_label = 'Sink'
    # Icon identifier
    bl_icon = 'SOUND'
    
    playback = Playback()
    
    internalTime = time.time()
    
    running = [True]
    
    def updateSound(self):
        if self.running[0]:
            try:
                self.playback.play_chunk(self.inputs[0].getData(self.internalTime, 41000, 1024/41000))
            except IndexError:
                pass
    t1 = None

    def updateLoop(self):

        while self.running[0]:
            self.internalTime = self.internalTime + 1024/41000
            self.updateSound()
            time.sleep(1024/41000/10)
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Audio")
        self.running[0] = True
        self.t1 = threading.Thread(target=self.updateLoop)
        self.t1.start()
    
    # Free function to clean up on removal.
    def free(self):
        self.running[0] = False
        print("Removing node ", self, ", Goodbye!")


### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class AudioNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'AudioTreeType'

# all categories in a list
node_categories = [
    # identifier, label, items list
    AudioNodeCategory("AUDIO_IN", "Inputs", items=[
        NodeItem("SineOscillatorNode"),
        NodeItem("SawOscillatorNode"),
        NodeItem("SquareOscillatorNode"),
        NodeItem("TriangleOscillatorNode"),
        NodeItem("NoiseGeneratorNode"),
    ]),
    AudioNodeCategory("AUDIO_OUT", "Outputs", items=[
        NodeItem("AudioSinkNode"),
    ]),
    AudioNodeCategory("AUDIO_OPERATORS", "Operators", items=[
        NodeItem("SignalSumNode"),
        NodeItem("SignalMulNode"),
    ]),
]


def register():
    
    try:
        unregister()
    except:
        pass
    
    bpy.utils.register_class(AudioTree)
    bpy.utils.register_class(RawAudioSocket)
    bpy.utils.register_class(Sine)
    bpy.utils.register_class(Sink)
    bpy.utils.register_class(Sum)
    bpy.utils.register_class(Saw)
    bpy.utils.register_class(Noise)
    bpy.utils.register_class(Square)
    bpy.utils.register_class(Triangle)
    bpy.utils.register_class(Mul)

    nodeitems_utils.register_node_categories("AUDIONODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("AUDIONODES")


    bpy.utils.unregister_class(AudioTree)
    bpy.utils.unregister_class(RawAudioSocket)
    bpy.utils.unregister_class(Sine)
    bpy.utils.unregister_class(Sink)
    bpy.utils.unregister_class(Sum)
    bpy.utils.unregister_class(Saw)
    bpy.utils.unregister_class(Noise)
    bpy.utils.unregister_class(Square)
    bpy.utils.unregister_class(Triangle)
    bpy.utils.register_class(Mul)


if __name__ == "__main__":
    register()
