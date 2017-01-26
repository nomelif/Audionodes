
import time

import bpy

from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat
from threading import Lock
from .painfuls import fix
from collections import deque
from threading import Thread

pygame, np, pyaudio = fix(("pygame", "numpy", "pyaudio"))

# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class AudioTree(NodeTree):

    '''Node tree for audio mixer'''

    bl_idname = 'AudioTreeType'
    bl_label = 'Audio nodes'
    bl_icon = 'PLAY_AUDIO'

    pygameInited =  [False]

    ch = [None]
    
    structureChanged = [False]
    
    sample_rate = 44100
    chunk_size = 1024


    def setupPygame(self):
            pygame.mixer.init(self.sample_rate, -16, 1, self.chunk_size)
            self.ch[0]=pygame.mixer.Channel(0)
            self.pygameInited[0] = True

    def play_chunk(self, internalTime, order, outputNode):
        if not self.pygameInited[0]:
            self.setupPygame()
        else:
            outputData = np.zeros(self.chunk_size)
            snd=pygame.sndarray.make_sound(np.int16(np.clip(outputData*(2**15), -2**15, 2**15-1)))
            self.ch[0].queue(snd)
    
    def reconstruct(self, order):
        order.clear()
        # Construct topological order of the node graph
        nodes = {}
        for node in self.nodes:
            connectedInputs = 0
            for socket in node.inputs:
                if socket.is_linked:
                    connectedInputs += 1
            nodes[node.name] = [node, connectedInputs]
            if connectedInputs == 0:
                order.append(node.name)
        
        for nodeName in order:
            node = nodes[nodeName][0]
            for socket in node.outputs:
                for link in socket.links:
                    nodes[link.to_node.name][1] -= 1
                    if nodes[link.to_node.name][1] == 0:
                        order.append(link.to_node.name)

    def needsAudio(self):
        try:
            if self.ch[0].get_queue() == None:
                return True
            else:
                return False
        except:
            return True
    
    def needsReconstruct(self):
        if self.structureChanged[0]:
            self.structureChanged[0] = False
            return True
        else:
            return False
    
    def update(self):
       self.structureChanged[0] = True

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



class Oscillator(AudioTreeNode):
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
        return (self.generate(phase, timeData=timeData, rate=rate, length=length) * self.inputs[1].getData(timeData, rate, length)[0] + self.inputs[2].getData(timeData, rate, length)[0], self.oscillatorStates[self.path_from_id()][0])
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Frequency (Hz)")
        self.inputs.new('RawAudioSocketType', "Amplitude")
        self.inputs[1].value_prop = 1.0
        self.inputs.new('RawAudioSocketType', "Offset")
        self.outputs.new('RawAudioSocketType', "Audio")

class MicrophoneGen():

    data = deque()

    def __init__(self, tree, bufferlen = 4):
        self.tree = tree
        self.bufferlen = bufferlen
        self.alive = True
        Thread(target=self.listen).start()

    def kill(self):
        self.alive = False

    def listen(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=self.tree.sample_rate, input=True, frames_per_buffer=self.tree.chunk_size)
        while self.alive:
            data = stream.read(self.tree.chunk_size)
            self.data.append(np.fromstring(data, dtype=np.int16).astype(np.float64)/65536)

    def __iter__(self):

        while self.alive:
            while len(self.data) < self.bufferlen:
                time.sleep(0.0001)
            while len(self.data) > self.bufferlen*2:
                self.data.popleft()
            yield self.data.popleft()


class Microphone(Node, AudioTreeNode):

    '''Record from a live microphone'''

    bl_idname = 'MicNode'

    bl_label = 'Microphone'

    data = {}

    def init(self,context):
        self.outputs.new('RawAudioSocketType', 'Sound')
        self.data[self.path_from_id()] = {}
        self.data[self.path_from_id()]["generator"] = MicrophoneGen(self.getTree())
        self.data[self.path_from_id()]["stamp"] = time.time()

    def free(self):
        self.data[self.path_from_id()]["generator"].kill()

    def callback(self, socket, timeData, rate, length):
        try:
            for part in self.data[self.path_from_id()]["generator"]:
                return (np.array([part]), np.array([self.data[self.path_from_id()]["stamp"]]))
        except KeyError:
            return (np.array([np.zeros(int(length*rate))]), np.array(time.time()))

class Piano(Node, AudioTreeNode):
    '''Map key presses to audio'''

    bl_idname = 'PianoNode'
    # Label for nice name display
    bl_label = 'Piano'

    keys = {}
    sustain = {}
    data = {}
    lock = {}

    def init(self, context):
        self.outputs.new('RawAudioSocketType', "Frequency")
        self.outputs.new('RawAudioSocketType', "Runtimes")
        self.outputs.new('RawAudioSocketType', "Velocities")
        self.keys[self.path_from_id()] = []
        self.sustain[self.path_from_id()] = False
        self.data[self.path_from_id()] = {"time":-1}
        self.lock[self.path_from_id()] = Lock()

    def parseEvent(self, event):

        self.lock[self.path_from_id()].acquire() # No one but me shall touch the notes

        currentTime = self.data[self.path_from_id()]["time"]

        if event["type"] == "key":

            if event["velocity"] != 0: # Press

                if self.sustain[self.path_from_id()]:

                    # Does the note already exist? If so, reactivate it

                    i = 0
                    found = False
                    while i < len(self.keys[self.path_from_id()]):
                        if self.keys[self.path_from_id()][i]["note"] == event["note"]:
                            self.keys[self.path_from_id()][i] = {"frequency":event["frequency"], "startTime":currentTime, "note":event["note"], "velocity":event["velocity"], "type":"pressed", "id":time.time()}
                            found = True
                        i = i + 1

                    if not found: # If no note is found, create a new one
                        self.keys[self.path_from_id()].append({"frequency":event["frequency"], "startTime":currentTime, "note":event["note"], "velocity":event["velocity"], "type":"pressed", "id":time.time()})
                else:

                    self.keys[self.path_from_id()].append({"frequency":event["frequency"], "startTime":currentTime, "note":event["note"], "velocity":event["velocity"], "type":"pressed", "id":time.time()})

            else: # Release

                if not self.sustain[self.path_from_id()]:

                    self.keys[self.path_from_id()] = list([key for key in self.keys[self.path_from_id()] if key["note"] != event["note"]])

                elif self.sustain[self.path_from_id()]:

                    i = 0
                    while i < len(self.keys[self.path_from_id()]): # Mark that the note is not pressed but only sustained
                        if self.keys[self.path_from_id()][i]["note"] == event["note"]:
                            self.keys[self.path_from_id()][i]["type"] = "sustain"
                        i = i + 1

        elif event["type"] == "sustain":

            if (event["velocity"] == 0) == self.sustain[self.path_from_id()]: # a velocity of zero means release; only run this if the state changes:
                self.sustain[self.path_from_id()] = not self.sustain[self.path_from_id()]
                if not self.sustain[self.path_from_id()]:

                    # Remove sustained notes

                    self.keys[self.path_from_id()] = list([key for key in self.keys[self.path_from_id()] if key["type"] != "sustain"])


        self.lock[self.path_from_id()].release()

    def clear(self):
        self.keys[self.path_from_id()] = []

    def draw_buttons(self, context, layout):
        layout.label("Node settings")
        layout.operator("audionodes.piano").caller_id = self.path_from_id()

    def callback(self, socket, timeIn, rate, length):

        if self.data[self.path_from_id()]["time"] != timeIn:

            self.lock[self.path_from_id()].acquire() # No one but me shall touch the notes

            if len(self.keys[self.path_from_id()]) == 0:

                self.data[self.path_from_id()] = {

                                                  "id": [0],
                                                  "frequency": np.array([[0]*int(rate*length)]),
                                                  "startTime": np.array([[0]*int(rate*length)]),
                                                  "velocity": np.array([[0]*int(rate*length)]),
                                                  "time": timeIn

                                                  }

            else:

                freqMap = []
                timeMap = []
                velocityMap = []
                stampMap = []

                for note in self.keys[self.path_from_id()]:
                    freqMap.append(note["frequency"])
                    timeMap.append(timeIn - note["startTime"])
                    velocityMap.append(note["velocity"]/127)
                    stampMap.append(note["id"])

                self.data[self.path_from_id()] = {

                                                  "id": np.array(stampMap),
                                                  "frequency": np.tile(np.array([freqMap]).transpose(), int(length*rate)),
                                                  "startTime": np.tile(np.array([timeMap]).transpose(), int(length*rate)),
                                                  "velocity": np.tile(np.array([velocityMap]).transpose(), int(length*rate)),
                                                  "time": timeIn

                                                  }

            self.lock[self.path_from_id()].release()

        if socket == self.outputs[0]:
            return (self.data[self.path_from_id()]["frequency"], self.data[self.path_from_id()]["id"])
        elif socket == self.outputs[1]:
            return (self.data[self.path_from_id()]["startTime"], self.data[self.path_from_id()]["id"])
        else:
            return (self.data[self.path_from_id()]["velocity"], self.data[self.path_from_id()]["id"])


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
