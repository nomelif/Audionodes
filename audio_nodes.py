import bpy
from bpy.types import NodeTree, Node, NodeSocket

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


    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.label(text)

    # Socket color
    def draw_color(self, context, node):
        return (0.607, 0.153, 0.702, 1.0)


# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class AudioTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AudioTreeType'


# Derived from the Node base type.
class Sine(Node, AudioTreeNode):
    # === Basics ===
    # Description string
    '''A sine wave generator'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SineGeneratorNode'
    # Label for nice name display
    bl_label = 'Sine'
    # Icon identifier
    bl_icon = 'SOUND'
    
    def update(self):
        print("Sine")
    
    def update_socket(self, context):
        self.outputs[0].links[0].to_node.update()
    
    my_input_value = bpy.props.FloatProperty(name="Frequency (Hz)", update = update_socket)
    
    def init(self, context):
        
        self.outputs.new('RawAudioSocketType', "Audio")



    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    def draw_buttons(self, context, layout):
        layout.prop(self, "my_input_value")


    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Sine"
    

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
    
    def update(self):
        print("Sink")
    
    def init(self, context):
        self.inputs.new('RawAudioSocketType', "Audio")

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")



    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Sink"


### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'AudioTreeType'

# all categories in a list
node_categories = [
    # identifier, label, items list
    MyNodeCategory("AUDIONODES", "Audio Nodes", items=[
        # our basic node
        NodeItem("SineGeneratorNode"),
        NodeItem("AudioSinkNode"),
        ])
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

    nodeitems_utils.register_node_categories("AUDIO_NODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("AUDIO_NODES")

    bpy.utils.unregister_class(AudioTree)
    bpy.utils.unregister_class(RawAudioSocket)
    bpy.utils.unregister_class(Sine)
    bpy.utils.unregister_class(Sink)


if __name__ == "__main__":
    register()
