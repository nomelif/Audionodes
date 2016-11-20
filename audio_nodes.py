import bpy
from bpy.types import NodeTree, Node, NodeSocket

# Implementation of custom nodes from Python


# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class AudioTree(NodeTree):
    # Description string
    '''A custom node tree type that will show up in the node editor header'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'AudioTreeType'
    # Label for nice name display
    bl_label = 'Audio nodes'
    # Icon identifier
    bl_icon = 'PLAY_AUDIO'


# Custom socket type
class MyCustomSocket(NodeSocket):
    # Description string
    '''Socket for raw audio'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'CustomSocketType'
    # Label for nice name display
    bl_label = 'Custom Node Socket'

    # Enum items list
    my_items = [
        ("DOWN", "Down", "Where your feet are"),
        ("UP", "Up", "Where your head should be"),
        ("LEFT", "Left", "Not right"),
        ("RIGHT", "Right", "Not left")
    ]

    myEnumProperty = bpy.props.EnumProperty(name="Direction", description="Just an example", items=my_items, default='UP')

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "myEnumProperty", text=text)

    # Socket color
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)


# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class MyCustomTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AudioTreeType'


# Derived from the Node base type.
class MyCustomNode(Node, MyCustomTreeNode):
    # === Basics ===
    # Description string
    '''A custom node'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'CustomNodeType'
    # Label for nice name display
    bl_label = 'Custom Node'
    # Icon identifier
    bl_icon = 'SOUND'

    # === Custom Properties ===
    # These work just like custom properties in ID data blocks
    # Extensive information can be found under
    # http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
    myStringProperty = bpy.props.StringProperty()
    myFloatProperty = bpy.props.FloatProperty(default=3.1415926)

    # === Optional Functions ===
    # Initialization function, called when a new node is created.
    # This is the most common place to create the sockets for a node, as shown below.
    # NOTE: this is not the same as the standard __init__ function in Python, which is
    #       a purely internal Python method and unknown to the node system!
    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Frequency (Hz)")

        self.outputs.new('NodeSocketColor', "How")

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")



    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "I am a custom node"


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
        NodeItem("CustomNodeType"),
        ])
    ]


def register():
    
    try:
        unregister()
    except:
        pass
    
    bpy.utils.register_class(AudioTree)
    bpy.utils.register_class(MyCustomSocket)
    bpy.utils.register_class(MyCustomNode)

    nodeitems_utils.register_node_categories("AUDIO_NODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("AUDIO_NODES")

    bpy.utils.unregister_class(AudioTree)
    bpy.utils.unregister_class(MyCustomSocket)
    bpy.utils.unregister_class(MyCustomNode)


if __name__ == "__main__":
    register()
