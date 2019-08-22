
import bpy
from bpy.types import Node
from .node_tree import AudioTreeNode

classes = []

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

    func_enum: bpy.props.EnumProperty(
        items = func_enum_items,
        update = change_func
    )
    
    anti_alias_check: bpy.props.BoolProperty(
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

classes.append(Oscillator)

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

    func_enum: bpy.props.EnumProperty(
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

classes.append(Math)

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

classes.append(Piano)

class Microphone(Node, AudioTreeNode):
    bl_idname = 'MicrophoneNode'
    bl_label = 'Microphone'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.outputs.new('RawAudioSocketType', "Input stream")

classes.append(Microphone)

class MidiTrigger(Node, AudioTreeNode):
    bl_idname = 'MidiTriggerNode'
    bl_label = 'MIDI Trigger'

    def update_props(self, context):
        self.send_property_update(0, self.channel)
        self.send_property_update(1, self.modes_to_native[self.interfaceType])

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.update_props(None)

    channel: bpy.props.IntProperty(name="Control", min=0, max=127, default=1, update=update_props)
    modes = [('TRIGGER_BUTTON', 'Trigger button', '', 0),
             ('KEY', 'Key', '', 1)]

    interfaceType: bpy.props.EnumProperty(
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

classes.append(MidiTrigger)

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

    mode: bpy.props.EnumProperty(
        items = modes,
        update = update_props
    )

    modes_to_native = { item[0]: item[3] for item in modes }

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.update_props(None)
        self.send_sound()


    sound: bpy.props.StringProperty(subtype='FILE_PATH', update=load_sound, get=None, set=None)
    sound_datablock: bpy.props.StringProperty(name="Sound Datablock")
    def draw_buttons(self, context, layout):
        layout.prop(self, "sound", text="")
        layout.prop(self, "mode", text="Mode")

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('TriggerSocketType', "Trigger")
        self.outputs.new('RawAudioSocketType', "Audio")
        self.update_props(None)
        self.send_sound()

classes.append(Sampler)

class Clock(Node, AudioTreeNode):
    bl_idname = 'ClockNode'
    bl_label = 'Clock'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Rate (BPM)")
        self.inputs[-1].value_prop = 120
        self.inputs.new('TriggerSocketType', "Run/stop")
        self.outputs.new('TriggerSocketType', "Trigger")

classes.append(Clock)

class TriggerEnvelope(Node, AudioTreeNode):
    bl_idname = 'TriggerEnvelopeNode'
    bl_label = 'Trigger Envelope'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('TriggerSocketType', "Trigger")
        self.inputs.new('RawAudioSocketType', "Delay time")
        self.inputs.new('RawAudioSocketType', "Attack time")
        self.inputs[-1].value_prop = 0.1
        self.inputs.new('RawAudioSocketType', "Hold time")
        self.inputs[-1].value_prop = 0.5
        self.inputs.new('RawAudioSocketType', "Hold level")
        self.inputs[-1].value_prop = 0.8
        self.inputs.new('RawAudioSocketType', "Attack slope")
        self.inputs[-1].value_prop = 0.5
        self.inputs.new('RawAudioSocketType', "Decay slope")
        self.inputs[-1].value_prop = 0.5
        self.inputs.new('RawAudioSocketType', "Release slope")
        self.inputs[-1].value_prop = 0.5
        self.outputs.new('RawAudioSocketType', "Envelope")

classes.append(TriggerEnvelope)

class Toggle(Node, AudioTreeNode):
    bl_idname = 'ToggleNode'
    bl_label = 'Toggle'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('TriggerSocketType', "Trigger")
        self.inputs.new('RawAudioSocketType', "A")
        self.inputs.new('RawAudioSocketType', "B")
        self.outputs.new('RawAudioSocketType', "Audio")

classes.append(Toggle)

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

classes.append(Delay)

class RandomAccessDelay(Node, AudioTreeNode):
    bl_idname = 'RandomAccessDelayNode'
    bl_label = 'Random Access Delay'

    def change_buffer(self, context):
        self.send_property_update(0, self.buffer_length)
    
    def reinit(self):
        AudioTreeNode.reinit(self)
        self.change_buffer(None)
    
    buffer_length: bpy.props.IntProperty(
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

classes.append(RandomAccessDelay)

class PitchBend(Node, AudioTreeNode):
    bl_idname = 'PitchBendNode'
    bl_label = 'Pitch Bend'

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('MidiSocketType', "MIDI")
        self.outputs.new('RawAudioSocketType', "Bend")

classes.append(PitchBend)

class Slider(Node, AudioTreeNode):
    bl_idname = 'SliderNode'
    bl_label = 'MIDI Control'


    def update_props(self, context):
        self.send_property_update(0, self.channel)
        self.send_property_update(1, self.modes_to_native[self.interfaceType])

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.update_props(None)

    channel: bpy.props.IntProperty(name="ID", min=1, max=16, default=1, update=update_props)
    modes = [('SLIDER', 'Slider', '', 0),
             ('KNOB', 'Knob', '', 1)]

    interfaceType: bpy.props.EnumProperty(
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

classes.append(Slider)

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

    method_enum: bpy.props.EnumProperty(
        items = method_enum_items,
        update = change_method
    )

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Audio")
        self.outputs.new('RawAudioSocketType', "Audio")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'method_enum', text='')

classes.append(Collapse)

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

    mode_enum: bpy.props.EnumProperty(
        items = mode_enum_items,
        update = update_props
    )
    poles: bpy.props.IntProperty(name="Biquads", min=0, max=6, default=2, update=update_props)

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

classes.append(IIRFilter)

class Noise(Node, AudioTreeNode):
    bl_idname = 'NoiseNode'
    bl_label = 'Noise'
    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Amplitude")
        self.inputs[0].value_prop = 1.0
        self.outputs.new('RawAudioSocketType', "Audio")

classes.append(Noise)

class Sink(Node, AudioTreeNode):
    bl_idname = 'SinkNode'
    bl_label = 'Sink'
    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('RawAudioSocketType', "Audio")

classes.append(Sink)
