
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
        # Blender likes to call this method when loading isn't yet finished,
        # don't do anything in that case
        if ffi.flag_loading_file:
            return
        links = ffi.begin_tree_update()
        for link in self.links:
            link.from_node.check_revive()
            link.to_node.check_revive()
            ffi.add_tree_update_link(links, link.from_node.get_uid(), link.to_node.get_uid(), link.from_socket.get_index(), link.to_socket.get_index())
        ffi.finish_tree_update(links)

    def post_load_handler(self):
        for node in self.nodes:
            node.reinit()
        self.update()


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
       self.node.send_value_update(self.get_index(), self.value_prop)

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

class TriggerSocket(NodeSocket, AudioTreeNodeSocket):
    '''Socket for trogger events'''
    bl_idname = 'TriggerSocketType'
    bl_label = 'Trigger'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.52734375, 0.99609375, 0.87109375, 1.0)

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class AudioTreeNode:
    bl_icon = 'SOUND'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AudioTreeType'

    def get_tree(self):
        return self.id_data

    def register_native(self):
        self["unique_id"] = ffi.create_node(self.bl_idname.encode('ascii'))

    def init(self, context):
        self.register_native()

    def send_value_update(self, index, value):
        self.check_revive()
        ffi.update_node_input_value(self.get_uid(), index, value)

    def send_property_update(self, index, value):
        self.check_revive()
        ffi.update_node_property_value(self.get_uid(), index, value)

    def reinit(self):
        self.register_native()
        for socket in self.inputs:
            if type(socket) == RawAudioSocket:
                socket.update_value(None)

    def copy(self, node):
        node.check_revive()
        self["unique_id"] = ffi.copy_node(node.get_uid(), self.bl_idname.encode('ascii'))

    def get_uid(self):
        return self["unique_id"]

    def free(self):
        if not ffi.node_exists(self.get_uid()):
            # Already freed
            return
        ffi.remove_node(self.get_uid())

    def check_revive(self):
        # Check if node was revived (e.g. undid a delete operation)
        if not ffi.node_exists(self.get_uid()):
            self.reinit()

    def send_binary(self, slot, data):
        ffi.send_node_binary_data(self.get_uid(), slot, data)


# Proof-of-concept state, remake? and move these to another file ASAP
class Oscillator(Node, AudioTreeNode):
    bl_idname = 'OscillatorNode'
    bl_label = 'Oscillator'

    def change_func(self, context):
        self.send_property_update(0, self.func_enum_to_native[self.func_enum])
        self.send_property_update(1, self.anti_alias_check)

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.change_func(None)

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
    
    anti_alias_check = bpy.props.BoolProperty(
        name = "Anti-alias",
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
        layout.prop(self, 'anti_alias_check')

class Math(Node, AudioTreeNode):
    bl_idname = 'MathNode'
    bl_label = 'Math'

    def change_func(self, context):
        self.send_property_update(0, self.func_enum_to_native[self.func_enum])

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.change_func(None)

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


class Microphone(Node, AudioTreeNode):
    bl_idname = 'MicrophoneNode'
    bl_label = 'Microphone'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.outputs.new('RawAudioSocketType', "Input stream")

class MidiTrigger(Node, AudioTreeNode):
    bl_idname = 'MidiTriggerNode'
    bl_label = 'MIDI Trigger'

    def update_props(self, context):
        self.send_property_update(0, self.channel)
        self.send_property_update(1, self.modes_to_native[self.interfaceType])

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.update_props(None)

    channel = bpy.props.IntProperty(name="Control", min=0, max=127, default=1, update=update_props)
    modes = [('TRIGGER_BUTTON', 'Trigger button', '', 0),
             ('KEY', 'Key', '', 1)]

    interfaceType = bpy.props.EnumProperty(
        items = modes,
        update = update_props
    )

    modes_to_native = { item[0]: item[3] for item in modes }

    def draw_buttons(self, context, layout):
        layout.prop(self, 'channel')
        layout.prop(self, 'interfaceType')


    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('MidiSocketType', "MIDI")
        self.outputs.new('TriggerSocketType', "Trigger")
        self.update_props(None)

class Sampler(Node, AudioTreeNode):
    bl_idname = 'SamplerNode'
    bl_label = 'Sampler'


    def update_props(self, context):
        self.send_property_update(0, self.modes_to_native[self.mode])
        if self.sound_datablock != "":
          sound_struct = bpy.data.sounds[self.sound_datablock]
          self.send_binary(0, sound_struct.packed_file.data)

    def load_sound(self, context):
        if self.sound_datablock != "":
          bpy.data.sounds[self.sound_datablock].use_memory_cache = False
          bpy.data.sounds[self.sound_datablock].use_fake_user = False
        sound_struct = bpy.data.sounds.load(filepath=self.sound)
        sound_struct.use_fake_user = True
        sound_struct.use_mono = True
        sound_struct.pack()
        sound_struct.use_memory_cache = True
        self.sound_datablock = sound_struct.name
        self.send_binary(0, sound_struct.packed_file.data)

    modes = [('RUN_ONCE', 'Run once', '', 0),
             ('LOOP', 'Loop', '', 1)]

    mode = bpy.props.EnumProperty(
        items = modes,
        update = update_props
    )

    modes_to_native = { item[0]: item[3] for item in modes }

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.update_props(None)


    sound = bpy.props.StringProperty(subtype='FILE_PATH', update=load_sound, get=None, set=None)
    sound_datablock = bpy.props.StringProperty(name="Sound Datablock")
    def draw_buttons(self, context, layout):
        layout.prop(self, "sound", text="")
        layout.prop(self, "mode")

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('TriggerSocketType', "Trigger")
        self.outputs.new('RawAudioSocketType', "Audio")
        self.update_props(None)

class Toggle(Node, AudioTreeNode):
    bl_idname = 'ToggleNode'
    bl_label = 'Toggle'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('TriggerSocketType', "Trigger")
        self.inputs.new('RawAudioSocketType', "A")
        self.inputs.new('RawAudioSocketType', "B")
        self.outputs.new('RawAudioSocketType', "Audio")


class PitchBend(Node, AudioTreeNode):
    bl_idname = 'PitchBendNode'
    bl_label = 'Pitch Bend'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('MidiSocketType', "MIDI")
        self.outputs.new('RawAudioSocketType', "Bend")

class Slider(Node, AudioTreeNode):
    bl_idname = 'SliderNode'
    bl_label = 'MIDI Control'


    def update_props(self, context):
        self.send_property_update(0, self.channel)
        self.send_property_update(1, self.modes_to_native[self.interfaceType])

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.update_props(None)

    channel = bpy.props.IntProperty(name="ID", min=1, max=16, default=1, update=update_props)
    modes = [('SLIDER', 'Slider', '', 0),
             ('KNOB', 'Knob', '', 1)]

    interfaceType = bpy.props.EnumProperty(
        items = modes,
        update = update_props
    )

    modes_to_native = { item[0]: item[3] for item in modes }

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('MidiSocketType', "MIDI")
        self.outputs.new('RawAudioSocketType', "Value")
        self.update_props(None)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'interfaceType')
        layout.prop(self, 'channel')

class Collapse(Node, AudioTreeNode):
    bl_idname = 'CollapseNode'
    bl_label = 'Collapse'

    def change_method(self, context):
        self.send_property_update(0, self.method_enum_to_native[self.method_enum])

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.change_method(None)

    method_enum_items = [
        ('ADD', 'Sum', '', 0),
        ('MIN', 'Minimum', '', 1),
        ('MAX', 'Maximum', '', 2),
        ('MUL', 'Product', '', 3),
    ]

    method_enum_to_native = { item[0]: item[3] for item in method_enum_items }

    method_enum = bpy.props.EnumProperty(
        items = method_enum_items,
        update = change_method
    )

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Audio")
        self.outputs.new('RawAudioSocketType', "Audio")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'method_enum', text='')

class IIRFilter(Node, AudioTreeNode):
    bl_idname = 'IIRFilterNode'
    bl_label = 'IIR Filter'

    def update_props(self, context):
        self.send_property_update(0, self.mode_enum_to_native[self.mode_enum])
        self.send_property_update(1, self.poles)

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.update_props(None)

    mode_enum_items = [
        ('LP', 'Low pass', '', 0),
        ('HP', 'High pass', '', 1),
    ]

    mode_enum_to_native = { item[0]: item[3] for item in mode_enum_items }

    mode_enum = bpy.props.EnumProperty(
        items = mode_enum_items,
        update = update_props
    )
    poles = bpy.props.IntProperty(name="Biquads", min=0, max=6, default=2, update=update_props)

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Input")
        self.inputs.new('RawAudioSocketType', "Cutoff (Hz)")
        self.inputs[1].value_prop = 1.0
        self.inputs.new('RawAudioSocketType', "Resonance")
        self.inputs[2].value_prop = 1.0
        self.inputs.new('RawAudioSocketType', "Rolloff")
        self.inputs[3].value_prop = 1.0
        self.outputs.new('RawAudioSocketType', "Audio")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'mode_enum', text='')
        layout.prop(self, 'poles')

class Noise(Node, AudioTreeNode):
    bl_idname = 'NoiseNode'
    bl_label = 'Noise'
    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Amplitude")
        self.inputs[0].value_prop = 1.0
        self.outputs.new('RawAudioSocketType', "Audio")

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
