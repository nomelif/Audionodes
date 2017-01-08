import bpy
from bpy.types import Node

from .painfuls import fix

pygame, np = fix()

from .node_tree import Oscillator
        


class Sine(Node, Oscillator):
    # Description string
    '''A sine wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SineOscillatorNode'
    # Label for nice name display
    bl_label = 'Sine'
    
    def generate(self, phase, **dataArgs):
        return np.sin(phase*np.pi*2)

    
class Saw(Node, Oscillator):
    # === Basics ===
    # Description string
    '''A saw wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SawOscillatorNode'
    # Label for nice name display
    bl_label = 'Saw'
    
    last_state = bpy.props.FloatProperty()
    
    def generate(self, phase, **dataArgs):
        return phase * 2 % 2 - 1
    
class Square(Node, Oscillator):
    # === Basics ===
    # Description string
    '''A square wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SquareOscillatorNode'
    # Label for nice name display
    bl_label = 'Square'
    
    def generate(self, phase, **dataArgs):
        pulseWidth = self.inputs[3].getData(**dataArgs)[0]
        return np.greater(phase % 1, 1 - pulseWidth) * 2 - 1
    
    def init(self, context):
        Oscillator.init(self, context)
        self.inputs.new('RawAudioSocketType', "Pulse width")
        self.inputs[3].value_prop = 0.5

class Triangle(Node, Oscillator):
    # === Basics ===
    # Description string
    '''A triangle wave oscillator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'TriangleOscillatorNode'
    # Label for nice name display
    bl_label = 'Triangle'
    
    def generate(self, phase, **dataArgs):
        return np.abs(phase * 4 % 4 - 2) - 1


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
