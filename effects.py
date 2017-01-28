import bpy
from bpy.types import Node

from .painfuls import fix

pygame, np = fix()

import time

from collections import deque

from .node_tree import AudioTreeNode
        


class DelayNode(Node, AudioTreeNode):
    '''Add a delayed echo to sound input'''
    
    def callback(self, inputSocketsData, timeData, rate, length):

        inputData = self.inputs[0].getData(inputSocketsData)[0].sum(axis=0)

        self.data[self.path_from_id()].append(inputData)
        while (len(self.data[self.path_from_id()])-1)*length > self.inputs[1].getData(inputSocketsData)[0][0][0]:

            self.data[self.path_from_id()].popleft()

        if len(self.data[self.path_from_id()])*length < self.inputs[1].getData(inputSocketsData)[0][0][0]:

            self.data[self.path_from_id()].append(inputData)
            return (np.array([inputData * (1-self.inputs[1].getData(inputSocketsData)[0][0][0])]), np.array([self.stamp[self.path_from_id()]]))
        else:
            newData = self.data[self.path_from_id()].popleft()
            result = newData * self.inputs[1].getData(inputSocketsData)[0][0][0] + inputData * (1 - self.inputs[1].getData(inputSocketsData)[0][0][0])
            self.data[self.path_from_id()].append(result)
            return ((np.array([result]), np.array([self.stamp[self.path_from_id()]])), )
                    
    
    bl_idname = 'DelayNode'
    # Label for nice name display
    bl_label = 'Delay'
    
    data = {}
    stamp = {}

    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Delay")
        self.inputs.new('RawAudioSocketType', "Factor")
        self.inputs[1].value_prop = 1.0
        self.outputs.new('RawAudioSocketType', "Audio")

        self.data[self.path_from_id()] = deque()
        self.stamp[self.path_from_id()] = time.time()
    
    
    def draw_buttons(self, context, layout):
        pass
    
   



def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
