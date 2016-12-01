"""
Class using Pyaudio for simple playback of raw audio-data represented by a float array.
The user only needs to create an object and call the play_chunk method.
 
"""



import time

import bpy
import numpy as np
from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat

import pygame

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
    
    bl_label = ''
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
        


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
