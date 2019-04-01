
import bpy

from bpy.types import NodeTree, Node, NodeSocket, Operator, PropertyGroup

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
        ffi.begin_tree_update()
        for link in self.links:
            if link.to_node.bl_idname == "NodeReroute":
                continue
            from_node, from_socket = link.from_node, link.from_socket
            to_node, to_socket = link.to_node, link.to_socket
            connected = True
            while from_node.bl_idname == "NodeReroute":
                if not from_node.inputs[0].is_linked:
                    connected = False
                    break
                new_link = from_node.inputs[0].links[0]
                from_node, from_socket = new_link.from_node, new_link.from_socket
            if not connected:
                continue
            from_node.check_revive()
            to_node.check_revive()
            ffi.add_tree_update_link(from_node.get_uid(), to_node.get_uid(), from_socket.get_index(), to_socket.get_index())
        ffi.finish_tree_update()

    def post_load_handler(self):
        for node in self.nodes:
            if isinstance(node, AudioTreeNode):
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
        if self["unique_id"] == -1:
            # better error type
            raise "Failed to register node with backend"

    def init(self, context):
        self.register_native()

    def send_value_update(self, index, value):
        self.check_revive()
        ffi.update_node_input_value(self.get_uid(), index, value)

    def send_property_update(self, index, value):
        self.check_revive()
        ffi.update_node_property_value(self.get_uid(), index, value)

    def get_configuration_options(self):
        self.check_revive()
        return ffi.get_configuration_options(self.get_uid())

    def set_configuration_option(self, name, val):
        self.check_revive()
        return ffi.set_configuration_option(self.get_uid(), name, val)

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
        self.inputs[-1].value_prop = 1.0
        self.inputs.new('RawAudioSocketType', "Offset")
        self.inputs.new('RawAudioSocketType', "Phase offset")
        self.inputs.new('RawAudioSocketType', "Parameter")
        self.inputs[-1].value_prop = 0.5
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


class MidiConfiguration(PropertyGroup):
    _prop_names = ['driver', 'portname', 'alsa_raw_device',
                   'jack_server', 'oss_device', 'win_device']
    driver = bpy.props.StringProperty()
    portname = bpy.props.StringProperty()
    alsa_raw_device = bpy.props.StringProperty()
    jack_server = bpy.props.StringProperty()
    oss_device = bpy.props.StringProperty()
    win_device = bpy.props.StringProperty()

midi_conf_node = None
midi_conf_valid_props = []
midi_conf_options = {
    'driver': [],
    'win_device': [],
}
midi_conf_option_descriptions = {
    'driver': {
        'alsa_raw': ('alsa_raw', 'ALSA raw', 'Linux only, use hardware directly'),
        'alsa_seq': ('alsa_seq', 'ALSA sequencer', 'Linux only, patch via aconnect or similar'),
        'coremidi': ('coremidi', 'CoreMIDI', 'macOS only'),
        'jack': ('jack', 'JACK', 'JACK Audio Connection Kit'),
        'midishare': ('midishare', 'MidiShare', ''),
        'oss': ('oss', 'OSS', 'Open Sound System'),
        'winmidi': ('winmidi', 'Windows MIDI', 'Windows only'),
    }
}

class MidiConfOperator(Operator):
    """MIDI Configuration popup for MidiInNode"""
    bl_idname = 'audionodes.configure_midi'
    bl_label = "MIDI Configuration"

    driver = bpy.props.EnumProperty(
        name = "Driver",
        items = lambda self, ctx: midi_conf_options['driver']
    )
    portname = bpy.props.StringProperty(
        name = "Port name",
        description = "Port name to be displayed in the patchbay",
        maxlen = 63
    )
    alsa_raw_device = bpy.props.StringProperty(
        name = "Device",
        description = "The MIDI device to connect to. See available options with e.g. `amidi -l`",
        maxlen = 255
    )
    jack_server = bpy.props.StringProperty(
        name = "JACK server",
        description = "Specify custom JACK server address, or leave empty for default",
        maxlen = 255
    )
    oss_device = bpy.props.StringProperty(
        name = "Device",
        description = "OSS device (file) to use",
        maxlen = 255
    )
    win_device = bpy.props.EnumProperty(
        name = "Device",
        description = "The MIDI device to connect to",
        items = lambda self, ctx: midi_conf_options['win_device']
    )

    def invoke(self, context, event):
        global midi_conf_node, midi_conf_options, midi_conf_valid_props
        midi_conf_node = context.node
        midi_conf_node.check_revive()
        if midi_conf_node["conf_fail"] and not midi_conf_node["conf_attempted"]:
            # UX: Initial config opened from file not working, reset
            midi_conf_node.set_configuration_option("reset_configuration", "")
        for name, val, opts in midi_conf_node.get_configuration_options():
            midi_conf_valid_props.append(name)
            if name in midi_conf_options:
                if name in midi_conf_option_descriptions:
                    midi_conf_options[name] = [
                        midi_conf_option_descriptions[name][opt] for opt in opts
                    ]
                else:
                    midi_conf_options[name] = [(opt, opt, '') for opt in opts]
            if val or name not in midi_conf_options:
                setattr(self, name, val)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "driver")
        if self.driver == 'alsa_raw':
            layout.prop(self, "alsa_raw_device")
        elif self.driver == 'alsa_seq':
            layout.prop(self, "portname")
        elif self.driver == 'coremidi':
            layout.prop(self, "portname")
        elif self.driver == 'jack':
            layout.prop(self, "jack_server")
        # No settings for midishare
        elif self.driver == 'oss':
            layout.prop(self, "oss_device")
        elif self.driver == 'winmidi':
            layout.prop(self, "win_device")
    def check(self, context):
        # Redraw needed when driver is changed
        return True

    def execute(self, context):
        global midi_conf_node, midi_conf_options, midi_conf_valid_props
        for name in midi_conf_valid_props:
            setattr(midi_conf_node.conf, name, getattr(self, name))
        midi_conf_node.apply_conf(context)
        midi_conf_node["conf_attempted"] = True
        midi_conf_node = None
        midi_conf_valid_props = []
        for lst in midi_conf_options.values():
            lst.clear()
        return {'FINISHED'}

class MidiIn(Node, AudioTreeNode):
    bl_idname = 'MidiInNode'
    bl_label = 'MIDI input'

    conf = bpy.props.PointerProperty(type=MidiConfiguration)

    def init_conf(self):
        for name, val, opts in self.get_configuration_options():
            setattr(self.conf, name, val)

    def apply_conf(self, context=None):
        for name in MidiConfiguration._prop_names:
            self.set_configuration_option(name, getattr(self.conf, name))
        self["conf_fail"] = self.set_configuration_option("apply_configuration", "") == 0
        if context: context.area.tag_redraw()

    def reinit(self):
        AudioTreeNode.reinit(self)
        self["conf_attempted"] = False
        self.apply_conf()

    def init(self, context):
        AudioTreeNode.init(self, context)
        self["conf_attempted"] = False
        self.init_conf()
        self.apply_conf(context)
        self.outputs.new('MidiSocketType', "Stream")

    def draw_buttons(self, context, layout):
        layout.operator("audionodes.configure_midi", "Configure MIDI")
        if "conf_fail" in self and self["conf_fail"]:
            layout.label("Configuration failed", icon='ERROR')

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
    
    def send_sound(self):
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
        # Unnecessary?
        # sound_struct.use_memory_cache = True
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
        self.send_sound()


    sound = bpy.props.StringProperty(subtype='FILE_PATH', update=load_sound, get=None, set=None)
    sound_datablock = bpy.props.StringProperty(name="Sound Datablock")
    def draw_buttons(self, context, layout):
        layout.prop(self, "sound", text="")
        layout.prop(self, "mode", text="Mode")

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('TriggerSocketType', "Trigger")
        self.outputs.new('RawAudioSocketType', "Audio")
        self.update_props(None)
        self.send_sound()

class Toggle(Node, AudioTreeNode):
    bl_idname = 'ToggleNode'
    bl_label = 'Toggle'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('TriggerSocketType', "Trigger")
        self.inputs.new('RawAudioSocketType', "A")
        self.inputs.new('RawAudioSocketType', "B")
        self.outputs.new('RawAudioSocketType', "Audio")

class Delay(Node, AudioTreeNode):
    bl_idname = 'DelayNode'
    bl_label = 'Delay'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Delay time (s)")
        self.inputs[1].value_prop = 1
        self.inputs.new('RawAudioSocketType', "Feedback")
        self.outputs.new('RawAudioSocketType', "Audio")

class RandomAccessDelay(Node, AudioTreeNode):
    bl_idname = 'RandomAccessDelayNode'
    bl_label = 'Random Access Delay'

    def change_buffer(self, context):
        self.send_property_update(0, self.buffer_length)
    
    def reinit(self):
        AudioTreeNode.reinit(self)
        self.change_buffer(None)
    
    buffer_length = bpy.props.IntProperty(
        name = "Buffer length (s)",
        update = change_buffer
    )
    
    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Audio")
        self.inputs.new('RawAudioSocketType', "Delay time (s)")
        self.inputs[1].value_prop = 1
        self.inputs.new('RawAudioSocketType', "Feedback")
        self.outputs.new('RawAudioSocketType', "Audio")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'buffer_length')

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
