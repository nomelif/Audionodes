import numpy as np

import bpy

from .node_tree import Oscillator
        


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


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
