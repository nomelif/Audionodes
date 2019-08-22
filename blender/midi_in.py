
import bpy
from bpy.types import Node, Operator, PropertyGroup
from .node_tree import AudioTreeNode

classes = []

class MidiConfiguration(PropertyGroup):
    _prop_names = ['driver', 'portname', 'alsa_raw_device',
                   'jack_server', 'oss_device', 'win_device']
    driver: bpy.props.StringProperty()
    portname: bpy.props.StringProperty()
    alsa_raw_device: bpy.props.StringProperty()
    jack_server: bpy.props.StringProperty()
    oss_device: bpy.props.StringProperty()
    win_device: bpy.props.StringProperty()

classes.append(MidiConfiguration)

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

    driver: bpy.props.EnumProperty(
        name = "Driver",
        items = lambda self, ctx: midi_conf_options['driver']
    )
    portname: bpy.props.StringProperty(
        name = "Port name",
        description = "Port name to be displayed in the patchbay",
        maxlen = 63
    )
    alsa_raw_device: bpy.props.StringProperty(
        name = "Device",
        description = "The MIDI device to connect to. See available options with e.g. `amidi -l`",
        maxlen = 255
    )
    jack_server: bpy.props.StringProperty(
        name = "JACK server",
        description = "Specify custom JACK server address, or leave empty for default",
        maxlen = 255
    )
    oss_device: bpy.props.StringProperty(
        name = "Device",
        description = "OSS device (file) to use",
        maxlen = 255
    )
    win_device: bpy.props.EnumProperty(
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
        return wm.invoke_props_dialog(operator=self)

    def draw(self, context):
        layout = self.layout
        layout.prop(data=self, property="driver")
        if self.driver == 'alsa_raw':
            layout.prop(data=self, property="alsa_raw_device")
        elif self.driver == 'alsa_seq':
            layout.prop(data=self, property="portname")
        elif self.driver == 'coremidi':
            layout.prop(data=self, property="portname")
        elif self.driver == 'jack':
            layout.prop(data=self, property="jack_server")
        # No settings for midishare
        elif self.driver == 'oss':
            layout.prop(data=self, property="oss_device")
        elif self.driver == 'winmidi':
            layout.prop(data=self, property="win_device")
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

classes.append(MidiConfOperator)

class MidiIn(Node, AudioTreeNode):
    bl_idname = 'MidiInNode'
    bl_label = 'MIDI input'

    conf: bpy.props.PointerProperty(type=MidiConfiguration)

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
        layout.operator(operator="audionodes.configure_midi", text="Configure MIDI")
        if "conf_fail" in self and self["conf_fail"]:
            layout.label(text="Configuration failed", icon='ERROR')

classes.append(MidiIn)
