
import bpy

from bpy.types import NodeTree, Node, NodeSocket

from . import ffi

class AudioTree(NodeTree):

    '''Node tree for audio mixer'''

    bl_idname = 'AudioTreeType'
    bl_label = 'Audio nodes'
    bl_icon = 'PLAY_AUDIO'

    def init(self):
        pass

    def update(self):
        links = ffi.native.begin_tree_update()
        for link in self.links:
            ffi.native.add_tree_update_link(links, link.from_node.get_uid(), link.to_node.get_uid(), link.from_socket.get_index(), link.to_socket.get_index())
        ffi.native.finish_tree_update(links)

    def send_value_update(self, node, index, value):
        ffi.native.update_node_input_value(node.get_uid(), index, value)

# Custom socket type
class AudioTreeNodeSocket:
    def get_tree(self):
        return self.id_data

    def get_index(self):
        return int(self.path_from_id().split('[')[-1][:-1])

class RawAudioSocket(NodeSocket, AudioTreeNodeSocket):
    '''Socket for raw audio'''
    bl_idname = 'RawAudioSocketType'
    bl_label = 'Raw Audio'

    def update_value(self, context):
       self.get_tree().send_value_update(self.node, self.get_index(), self.value_prop)

    value_prop = bpy.props.FloatProperty(update=update_value)

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "value_prop", text=text)

    def draw_color(self, context, node):
        return (0.607, 0.153, 0.702, 1.0)

class MidiSocket(NodeSocket, AudioTreeNodeSocket):
    '''Socket for MIDI events'''
    bl_idname = 'MidiSocketType'
    bl_label = 'MIDI'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.9, 0.86, 0.14, 1.0)

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class AudioTreeNode:
    bl_icon = 'SOUND'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AudioTreeType'

    def get_tree(self):
        return self.id_data

    def init(self, context):
        self["unique_id"] = ffi.native.create_node(self.bl_idname.encode('ascii'))

    def copy(self, node):
        self["unique_id"] = ffi.native.copy_node(node.get_uid(), self.bl_idname.encode('ascii'))

    def get_uid(self):
        return self["unique_id"];

    def free(self):
        ffi.native.remove_node(self.get_uid())

# Proof-of-concept state, remake and move these to another file ASAP
class Oscillator(Node, AudioTreeNode):
    bl_idname = 'OscillatorNode'
    bl_label = 'Oscillator'

    def change_func(self, context):
        ffi.native.update_node_property_value(self.get_uid(), 0, self.func_enum_to_native[self.func_enum])

    func_enum_items = [
        ('SIN', 'Sine', '', 0),
        ('SAW', 'Saw', '', 1),
        ('SQR', 'Square', '', 2),
        ('TRI', 'Triangle', '', 3),
    ]

    func_enum_to_native = { item[0]: item[3] for item in func_enum_items }

    func_enum = bpy.props.EnumProperty(
        items = func_enum_items,
        update = change_func
    )

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Frequency (Hz)")
        self.inputs.new('RawAudioSocketType', "Amplitude")
        self.inputs[1].value_prop = 1.0
        self.inputs.new('RawAudioSocketType', "Offset")
        self.inputs.new('RawAudioSocketType', "Parameter")
        self.inputs[3].value_prop = 0.5
        self.outputs.new('RawAudioSocketType', "Audio")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'func_enum', text='')

class Math(Node, AudioTreeNode):
    bl_idname = 'MathNode'
    bl_label = 'Math'

    def change_func(self, context):
        ffi.native.update_node_property_value(self.get_uid(), 0, self.func_enum_to_native[self.func_enum])

    func_enum_items = [
        ('ADD', 'Add', '', 0),
        ('SUB', 'Subtract', '', 1),
        ('MUL', 'Multiply', '', 2),
        ('DIV', 'Divide', '', 3),
        ('SIN', 'Sine', '', 4),
        ('COS', 'Cosine', '', 5),
        ('TAN', 'Tangent', '', 6),
        ('ASIN', 'Arcsine', '', 7),
        ('ACOS', 'Arccosine', '', 8),
        ('ATAN', 'Arctangent', '', 9),
        ('POW', 'Power', '', 10),
        ('LOG', 'Logarithm', '', 11),
        ('MIN', 'Minimum', '', 12),
        ('MAX', 'Maximum', '', 13),
        ('RND', 'Round', '', 14),
        ('LT', 'Less Than', '', 15),
        ('GT', 'Greater Than', '', 16),
        ('MOD', 'Modulo', '', 17),
        ('ABS', 'Absolute', '', 18)
    ]

    func_enum_to_native = { item[0]: item[3] for item in func_enum_items }

    func_enum = bpy.props.EnumProperty(
        items = func_enum_items,
        update = change_func
    )

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Audio")
        self.outputs.new('RawAudioSocketType', "Result")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'func_enum', text='')

class MidiIn(Node, AudioTreeNode):
    bl_idname = 'MidiInNode'
    bl_label = 'MIDI input'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.outputs.new('MidiSocketType', "Stream")

class Piano(Node, AudioTreeNode):
    bl_idname = 'PianoNode'
    bl_label = 'Piano'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('MidiSocketType', "MIDI")
        self.inputs.new('RawAudioSocketType', "Decay time")
        self.outputs.new('RawAudioSocketType', "Frequency")
        self.outputs.new('RawAudioSocketType', "Velocity")
        self.outputs.new('RawAudioSocketType', "Runtime")
        self.outputs.new('RawAudioSocketType', "Decay")

class PitchBend(Node, AudioTreeNode):
    bl_idname = 'PitchBendNode'
    bl_label = 'Pitch Bend'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('MidiSocketType', "MIDI")
        self.outputs.new('RawAudioSocketType', "Bend")

class Sink(Node, AudioTreeNode):
    bl_idname = 'SinkNode'
    bl_label = 'Sink'
    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Audio")


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
