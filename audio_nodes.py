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
    last_value = {}
    
    cache = {}
    
    def getData(self, time, rate, length):
        
        if self.is_output and self.path_from_id() in self.cache.keys():
            if self.cache[self.path_from_id()]["time"] == time and self.cache[self.path_from_id()]["rate"] == rate and self.cache[self.path_from_id()]["length"] == length:
                return self.cache[self.path_from_id()]["data"]
        
        new_data = None
        
        if self.is_output:
            new_data = self.node.callback(self, time, rate, length)
        elif self.is_linked:
            new_data = self.links[0].from_socket.getData(time, rate, length)
        else:
            last_value = 0
            if self.path_from_id() in self.last_value:
                last_value = self.last_value[self.path_from_id()]
            self.last_value[self.path_from_id()] = self.value_prop
            coeff = np.arange(int(length*rate))/(length*rate)
            new_data = np.array([self.value_prop * coeff + last_value * (1-coeff)])
        
        if self.is_output:
            self.cache[self.path_from_id()] = {"time":time, "rate":rate, "length":length, "data":new_data}
        
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
    
    def getTree(self):
        return self.id_data

class Oscillator(Node, AudioTreeNode):
    '''Framework for an oscillator node. Just add a generator!'''
    
    oscillatorStates = {}
    
    def callback(self, socket, time, rate, length):
        output = None
        
        # Possible optimization:
        
        #if np.count_nonzero(self.inputs[0].getData(time, rate, length)) == 0 or np.count_nonzero(self.inputs[0].getData(time, rate, length)) == 0:
        #    return np.full(int(rate*length), 0.0 + self.inputs[2].getData(time, rate, length))

        rebuildCache = False
        
        try:
        
            if len(self.oscillatorStates[self.path_from_id()]) != len(self.inputs[0].getData(time, rate, length)):
                rebuildCache = True

        except KeyError:
            rebuildCache = True
        
        if rebuildCache:
            self.oscillatorStates[self.path_from_id()] = np.array([np.zeros(len(self.inputs[0].getData(time, rate, length)))])

       
        freq = self.inputs[0].getData(time, rate, length)
        phase = ((freq.cumsum(axis=1)/rate).transpose() + self.oscillatorStates[self.path_from_id()]).transpose()
        self.oscillatorStates[self.path_from_id()] = (phase[:,-1] % 1)
        return self.generate(phase) * self.inputs[1].getData(time, rate, length) + self.inputs[2].getData(time, rate, length)
    
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
        if not key in self.keys[self.path_from_id()]:
            self.keys[self.path_from_id()].append(key)
    
    def clear(self):
        self.keys[self.path_from_id()] = []
    
    def getKey(self):
        return self.keys[self.path_from_id()][0]
    
    def removeKey(self, key):
        try:
            self.keys[self.path_from_id()].remove(key)
        except ValueError:
            pass
    
    def draw_buttons(self, context, layout):
        layout.label("Node settings")
        layout.operator("audionodes.piano").caller_id = self.path_from_id()
    
    def callback(self, socket, time, rate, length):
        
        if len(self.keys[self.path_from_id()][0]) != 0:
            frequencies = {"§":261.63, "1":277.18, "2":293.66, "3":311.13, "4":329.63, "5":349.23, "6":369.99, "7":392.00, "8":415.30, "9":440.00, "0":466.16, "+":493.88}
            try:
                
                freqMap = []
                for freq in self.keys[self.path_from_id()]:
                    freqMap.append(frequencies[freq])
                print(freqMap)
                return np.tile(np.array([freqMap]).transpose(), int(length*rate))
            except KeyError:
                return np.array([[0]*int(rate*length)])
        else:
            return np.array([[0]*int(rate*length)])
        
        

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
        return np.array([np.random.rand(rate*length)])
    
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
                self.playback.play_chunk(self.inputs[0].getData(self.internalTime, 41000, 1024/41000).sum(axis=0))
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


class PianoCapture(bpy.types.Operator):
    bl_idname = "audionodes.piano"
    bl_label = "Keyboard capture"
    
    caller_id = bpy.props.StringProperty()
    caller = None
    
    def __init__(self):
        print("Start")

    def __del__(self):
        self.caller.clear()
        print("End")

    def modal(self, context, event):
        if event.type == 'ESC':
            self.caller.clear()
            return {'FINISHED'}
        
        elif event.value == "RELEASE":
            try:
                self.caller.removeKey(("§", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+")[("NONE", "NUMPAD_0", "NUMPAD_1", "NUMPAD_2", "NUMPAD_3", "NUMPAD_4", "NUMPAD_5", "NUMPAD_6", "NUMPAD_7", "NUMPAD_8", "NUMPAD_9", "PLUS").index(event.type)])
            except ValueError:
                pass
        elif event.unicode in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "+", "§"):

            if event.type == "BACK_SPACE":
                self.caller.setKey("BACK_SPACE")
            else:
                self.caller.setKey(event.unicode)
        else:
            #print(event.unicode)
            pass

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        tree = context.active_node.getTree()
        
        caller = None
        for node in tree.nodes:
            if node.path_from_id() == self.caller_id:
                caller = node
                break
        
        self.caller = caller
        
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
    bpy.utils.unregister_class(Piano)


if __name__ == "__main__":
    register()
