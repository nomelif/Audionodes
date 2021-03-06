
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

    def send_sound(self, context):
        if self.sound != None:
            self.sound.pack()
            self.send_binary(0, self.sound.packed_file.data)
        else:
            # Empty file works for now (until there's proper error handling on the other end)
            self.send_binary(0, bytes())

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
        self.send_sound(None)


    sound: bpy.props.PointerProperty(name="Sound (WAV)", type=bpy.types.Sound, update=send_sound)
    def draw_buttons(self, context, layout):
        layout.template_ID(self, "sound", open="SOUND_OT_open")
        layout.prop(self, "mode", text="Mode")

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('TriggerSocketType', "Trigger")
        self.outputs.new('RawAudioSocketType', "Audio")
        self.update_props(None)

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

SEQUENCER_MAX_STEPS = 128
def trigger_sequencer_list_update(self, context):
    context.node.change_list(context)
class TriggerSequencerList(bpy.types.PropertyGroup):
    __annotations__ = {f"step{i}": bpy.props.BoolProperty(name=f"Step {i+1}", update=trigger_sequencer_list_update) for i in range(SEQUENCER_MAX_STEPS)}
classes.append(TriggerSequencerList)

class TriggerSequencer(Node, AudioTreeNode):
    bl_idname = 'TriggerSequencerNode'
    bl_label = 'Trigger Sequencer'
    bl_width_min = 70.0

    def change_list(self, context):
        buf = bytearray(self.step_amount)
        for i in range(self.step_amount):
            buf[i] = getattr(self.sequence, f"step{i}")
        self.send_binary(0, bytes(buf))

    step_amount: bpy.props.IntProperty(name="Steps", default=16, min=1, max=SEQUENCER_MAX_STEPS, update=change_list)
    sequence: bpy.props.PointerProperty(type=TriggerSequencerList, name="Sequence")

    current_step: bpy.props.IntProperty(default=0)

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('TriggerSocketType', "Trigger")
        self.outputs.new('TriggerSocketType', "Trigger")
        self.change_list(None)

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.change_list(None)

    def receive_message(self, slot, value):
        if slot == 0:
            self.current_step = value
            # Force a redraw of the node
            self.name = self.name

    def draw_buttons(self, context, layout):
        layout.prop(self, "step_amount")
        grid = layout.grid_flow(row_major=True)
        x = self.current_step-1
        for i in range(self.step_amount):
            l = grid.row()
            l.alignment = 'CENTER'
            if i == x:
                l.alert = True
            l.prop(self.sequence, f"step{i}", text="", icon_only=True)


classes.append(TriggerSequencer)

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

class MIDIControl(Node, AudioTreeNode):
    bl_idname = 'MIDIControlNode'
    bl_label = 'MIDI Control'

    def update_props(self, context):
        self.send_property_update(0, self.channel)
        self.send_property_update(1, self.cc_no)

    def reinit(self):
        AudioTreeNode.reinit(self)
        self.update_props(None)

    channel: bpy.props.IntProperty(name="Channel", description="Set to 0 to listen to all channels", min=0, max=16, default=0, update=update_props)
    cc_no: bpy.props.IntProperty(name="CC #", min=0, max=127, default=70, update=update_props)

    def init(self, context):
        AudioTreeNode.init(self, context)
        self.inputs.new('MidiSocketType', "MIDI")
        self.outputs.new('RawAudioSocketType', "Value")
        self.update_props(None)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'channel')
        layout.prop(self, 'cc_no')

classes.append(MIDIControl)

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
