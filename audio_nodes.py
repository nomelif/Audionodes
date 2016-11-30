# Blender addon sorcery

bl_info = {"name": "Audionodes", "description":"Create complex soundscapes in real time using nodes.", "author":"Roope Salmi, Théo Friberg", "version":(0,1), "blender":(2,77,0), "location":"Node Editor > Sound Icon > Add new", "warning":"Very much alpha, may blow up in your face.", "category": "Node", "tracker_url":"https://github.com/nomelif/Audionodes/issues", "wiki_url":"https://github.com/nomelif/Audionodes"}


import bpy
import numpy as np
import time
from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat

from struct import pack
from array import array

import threading

import wave
import struct
import tempfile
import pygame
import aud
 
"""
Class using Pyaudio for simple playback of raw audio-data represented by a float array.
The user only needs to create an object and call the play_chunk method.
 
"""


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
    
    pygameInited =  [False]
    
    ch = [None]
    
    def setupPygame(self):
            SRATE=41000 # sample rate in Hz
            pygame.mixer.init(SRATE, -16, 1, 1024)
            self.ch[0]=pygame.mixer.Channel(0)
            self.pygameInited[0] = True
        
    def play_chunk(self, inputData):
        if not self.pygameInited[0]:
            self.setupPygame()
        else:
            snd=pygame.sndarray.make_sound(np.int16(inputData*(2**15)))
            self.ch[0].queue(snd)
    
    def needsAudio(self):
        try:
            if self.ch[0].get_queue() == None:
                return True
            else:
                return False
        except:
            return True
    


# Custom socket type
class RawAudioSocket(NodeSocket):
    # Description string
    '''Socket for raw audio'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'RawAudioSocketType'
    # Label for nice name display
    bl_label = 'Raw Audio'
    
    value_prop = bpy.props.FloatProperty()
    last_value = {}
    
    cache = {}
    
    def getData(self, timeData, rate, length):
        
        if self.is_output and self.path_from_id() in self.cache.keys():
            if self.cache[self.path_from_id()]["time"] == timeData and self.cache[self.path_from_id()]["rate"] == rate and self.cache[self.path_from_id()]["length"] == length:
                return self.cache[self.path_from_id()]["data"]
        
        new_data = None
        
        if self.is_output:
            new_data = self.node.callback(self, timeData, rate, length)
        elif self.is_linked:
            new_data = self.links[0].from_socket.getData(timeData, rate, length)
        else:
            last_value = 0
            if self.path_from_id() in self.last_value:
                last_value = self.last_value[self.path_from_id()][0]
            self.last_value[self.path_from_id()] = (self.value_prop, time.time())
            coeff = np.arange(int(length*rate))/(length*rate)
            new_data = (np.array([self.value_prop * coeff + last_value * (1-coeff)]), np.array([self.last_value[self.path_from_id()][1]]))
        
        if self.is_output:
            self.cache[self.path_from_id()] = {"time":timeData, "rate":rate, "length":length, "data":new_data}
        
        return new_data
    
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "value_prop", text=text)

    
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
    
    def getTree(self):
        return self.id_data

class Oscillator(Node, AudioTreeNode):
    '''Framework for an oscillator node. Just add a generator!'''
    
    oscillatorStates = {}
    
    def callback(self, socket, timeData, rate, length):
        output = None
        
        # Possible optimization:
        
        #if np.count_nonzero(self.inputs[0].getData(time, rate, length)) == 0 or np.count_nonzero(self.inputs[0].getData(time, rate, length)) == 0:
        #    return np.full(int(rate*length), 0.0 + self.inputs[2].getData(time, rate, length))

        rebuildCache = False

        try:
        
            if len(self.oscillatorStates[self.path_from_id()][0]) != len(self.inputs[0].getData(timeData, rate, length)[0]):
                rebuildCache = True

        except KeyError:
            self.oscillatorStates[self.path_from_id()] = [np.array([]), np.array([])]
            rebuildCache = True
        
        if rebuildCache:
            
            # Remove extra shit
            
            for key in self.oscillatorStates[self.path_from_id()][1]:
                if not key in self.inputs[0].getData(timeData, rate, length)[1]:
                    index = np.where(self.oscillatorStates[self.path_from_id()][1]==key)
                    self.oscillatorStates[self.path_from_id()][1] = np.delete(self.oscillatorStates[self.path_from_id()][1], index)
                    self.oscillatorStates[self.path_from_id()][0] = np.delete(self.oscillatorStates[self.path_from_id()][0], index)
            
            # Add signals that are lacking
            for index in range(len(self.inputs[0].getData(timeData, rate, length)[1])):
                
                if not (len(self.oscillatorStates[self.path_from_id()][1]) > index and self.oscillatorStates[self.path_from_id()][1][index] == self.inputs[0].getData(timeData, rate, length)[1][index]):
                    self.oscillatorStates[self.path_from_id()][0] = np.insert(self.oscillatorStates[self.path_from_id()][0], index, 0, axis=0)
                    self.oscillatorStates[self.path_from_id()][1] = np.insert(self.oscillatorStates[self.path_from_id()][1], index, self.inputs[0].getData(timeData, rate, length)[1][index], axis=0)
            
            
        freq = self.inputs[0].getData(timeData, rate, length)[0]
        phase = ((freq.cumsum(axis=1)/rate).transpose() + self.oscillatorStates[self.path_from_id()][0]).transpose()
        self.oscillatorStates[self.path_from_id()][0] = (phase[:,-1] % 1)
        return (self.generate(phase) * self.inputs[1].getData(timeData, rate, length)[0] + self.inputs[2].getData(timeData, rate, length)[0], self.oscillatorStates[self.path_from_id()][0])
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Frequency (Hz)")
        self.inputs.new('RawAudioSocketType', "Range")
        self.inputs[1].value_prop = 1.0
        self.inputs.new('RawAudioSocketType', "Offset")
        self.outputs.new('RawAudioSocketType', "Audio")

class Piano(Node, AudioTreeNode):
    '''Map key presses to audio.'''
    
    def callback(self, socket, time, rate, length):
        return np.zeros(rate*length)
    
    bl_idname = 'PianoNode'
    # Label for nice name display
    bl_label = 'Piano'
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        self.keys[self.path_from_id()] = []
    
    keys = {}
    
    def setKey(self, key):
        
        # Exit if the key is already known
        
        for knownKey in self.keys[self.path_from_id()]:
            if knownKey[0] == key:
                return None
        self.keys[self.path_from_id()].append((key, time.time()))
    
    def clear(self):
        self.keys[self.path_from_id()] = []
    
    def getKey(self):
        return self.keys[self.path_from_id()][0]
    
    def removeKey(self, key):
        i = 0
        for knownKey in self.keys[self.path_from_id()]:
            if knownKey[0] == key:
                del self.keys[self.path_from_id()][i]
                break
            i = i + 1
    
    def draw_buttons(self, context, layout):
        layout.label("Node settings")
        layout.operator("audionodes.piano").caller_id = self.path_from_id()
    
    def callback(self, socket, time, rate, length):
        
        if len(self.keys[self.path_from_id()][0]) != 0:
            frequencies = {"§":261.63, "1":277.18, "2":293.66, "3":311.13, "4":329.63, "5":349.23, "6":369.99, "7":392.00, "8":415.30, "9":440.00, "0":466.16, "+":493.88}
            try:
                
                freqMap = []
                for freq in self.keys[self.path_from_id()]:
                    freqMap.append(frequencies[freq[0]])
                
                stampMap = []
                for freq in self.keys[self.path_from_id()]:
                    stampMap.append(freq[1])
                
                return (np.tile(np.array([freqMap]).transpose(), int(length*rate)), np.array(stampMap))
            except KeyError:
                return (np.array([[0]*int(rate*length)]), [0])
        else:
            return (np.array([[0]*int(rate*length)]), [0])
        
        

class Sine(Oscillator):
    # Description string
    '''A sine wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SineOscillatorNode'
    # Label for nice name display
    bl_label = 'Sine'
    
    def generate(self, phase):
        return np.sin(phase*np.pi*2)

    
class Saw(Oscillator):
    # === Basics ===
    # Description string
    '''A saw wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SawOscillatorNode'
    # Label for nice name display
    bl_label = 'Saw'
    
    last_state = bpy.props.FloatProperty()
    
    def generate(self, phase):
        return phase * 2 % 2 - 1
    
class Square(Oscillator):
    # === Basics ===
    # Description string
    '''A square wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SquareOscillatorNode'
    # Label for nice name display
    bl_label = 'Square'
    
    def generate(self, phase):
        return np.greater(phase % 1, 0.5) * 2 - 1

class Triangle(Oscillator):
    # === Basics ===
    # Description string
    '''A triangle wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'TriangleOscillatorNode'
    # Label for nice name display
    bl_label = 'Triangle'
    
    def generate(self, phase):
        return np.abs(phase * 4 % 4 - 2) - 1
    
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
        return (np.array([np.random.rand(rate*length)]), np.array(self.stamps[self.path_from_id()]))
    
    stamps = {}
    
    def init(self, context):
        self.stamps[self.path_from_id()] = time.time()
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
        
        return (data_1[0] + data_2[0], data_1[1])
    
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
        
        return (data_1[0] * data_2[0], data_1[1])
    
    def init(self, context):
        
        self.outputs.new('RawAudioSocketType', "Audio")
        
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

class Max(Node, AudioTreeNode):
    '''Maximum of two signals'''
    bl_idname = 'SignalMaxNode'
    bl_label = 'Max'
    
    def callback(self, socketId, time, rate, length):
        data_1 = self.inputs[0].getData(time, rate, length)
        data_2 = self.inputs[1].getData(time, rate, length)
        return (np.maximum(data_1[0], data_2[0]), data_1[1])
    
    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")

class Min(Node, AudioTreeNode):
    '''Minimum of two signals'''
    bl_idname = 'SignalMinNode'
    bl_label = 'Min'
    
    def callback(self, socketId, time, rate, length):
        data_1 = self.inputs[0].getData(time, rate, length)
        data_2 = self.inputs[1].getData(time, rate, length)
        return (np.minimum(data_1[0], data_2[0]), data_1[1])
    
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
    
    internalTime = time.time()
    
    running = [True]
    
    def updateSound(self):
        if self.running[0]:
            try:
                self.getTree().play_chunk(self.inputs[0].getData(self.internalTime, 41000, 1024/41000)[0].sum(axis=0))
            except IndexError:
                pass
    t1 = None

    def updateLoop(self):

        while self.running[0]:
            if self.getTree().needsAudio():
                self.internalTime = self.internalTime + 1024/41000
                self.updateSound()
            time.sleep(0.01)
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Audio")
        self.running[0] = True
        self.t1 = threading.Thread(target=self.updateLoop)
        self.t1.start()
    
    # Free function to clean up on removal.
    def free(self):
        self.running[0] = False


class PianoCapture(bpy.types.Operator):
    bl_idname = "audionodes.piano"
    bl_label = "Keyboard capture"
    
    caller_id = bpy.props.StringProperty()
    caller = [None]

    def __del__(self):
        try:
            self.caller[0].clear()
        except:
            pass

    def modal(self, context, event):
        if event.type == 'ESC':
            self.caller[0].clear()
            return {'FINISHED'}
        
        elif event.value == "RELEASE":
            try:
                self.caller[0].removeKey(("§", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+")[("NONE", "NUMPAD_0", "NUMPAD_1", "NUMPAD_2", "NUMPAD_3", "NUMPAD_4", "NUMPAD_5", "NUMPAD_6", "NUMPAD_7", "NUMPAD_8", "NUMPAD_9", "PLUS").index(event.type)])
            except ValueError:
                pass
        else:
            try:
                if event.unicode in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "+", "§"):
                    self.caller[0].setKey(event.unicode)
            except UnicodeDecodeError:
                pass

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        tree = context.active_node.getTree()
        
        caller = None
        for node in tree.nodes:
            if node.path_from_id() == self.caller_id:
                caller = node
                break
        
        self.caller[0] = caller
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

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
        NodeItem("PianoNode"),
    ]),
    AudioNodeCategory("AUDIO_OUT", "Outputs", items=[
        NodeItem("AudioSinkNode"),
    ]),
    AudioNodeCategory("AUDIO_OPERATORS", "Operators", items=[
        NodeItem("SignalSumNode"),
        NodeItem("SignalMulNode"),
        NodeItem("SignalMaxNode"),
        NodeItem("SignalMinNode"),
    ]),
]


def register():
    
    try:
        unregister()
    except:
        pass
    
    bpy.utils.register_class(PianoCapture)
    
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
    bpy.utils.register_class(Max)
    bpy.utils.register_class(Min)
    bpy.utils.register_class(Piano)

    nodeitems_utils.register_node_categories("AUDIONODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("AUDIONODES")

    bpy.utils.unregister_class(PianoCapture)

    bpy.utils.unregister_class(AudioTree)
    bpy.utils.unregister_class(RawAudioSocket)
    bpy.utils.unregister_class(Sine)
    bpy.utils.unregister_class(Sink)
    bpy.utils.unregister_class(Sum)
    bpy.utils.unregister_class(Saw)
    bpy.utils.unregister_class(Noise)
    bpy.utils.unregister_class(Square)
    bpy.utils.unregister_class(Triangle)
    bpy.utils.unregister_class(Mul)
    bpy.utils.unregister_class(Max)
    bpy.utils.unregister_class(Min)
    bpy.utils.unregister_class(Piano)


if __name__ == "__main__":
    register()
