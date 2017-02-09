import bpy
from bpy.types import Node

from bpy.props import IntProperty

from .painfuls import fix
pygame, np = fix()

from .node_tree import AudioTreeNode

class Sequencer(Node, AudioTreeNode):
    '''Output one of many inputs at a time'''
    bl_idname = 'SequencerNode'
    bl_label = 'Sequencer'
    
    def update_steps(self, context):
        while len(self.inputs)-1 > self.steps:
            self.inputs.remove(self.inputs[-1])
        while len(self.inputs)-1 < self.steps:
            self.inputs.new('RawAudioSocketType', "Step")
    steps = IntProperty(min=1, default=4, name="Steps", update=update_steps)
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Current step")
        self.outputs.new('RawAudioSocketType', "Output")
        self.update_steps(context)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'steps')
        
    def callback(self, inputSocketsData, time, rate, length):
        current_step, stamps = self.inputs[0].getData(inputSocketsData)
        result = np.zeros_like(current_step)
        for i in range(1, len(self.inputs)):
            result += (np.floor(current_step*self.steps) == (i-1))*self.inputs[i].getData(inputSocketsData)[0]
        return ((result, stamps), )
