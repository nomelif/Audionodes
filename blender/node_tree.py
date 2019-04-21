
import bpy
from bpy.types import NodeTree, Node, NodeSocket, Operator

from . import ffi

classes = []

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

classes.append(AudioTree)

# Custom socket type (mixin)
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

classes.append(RawAudioSocket)

class MidiSocket(NodeSocket, AudioTreeNodeSocket):
    '''Socket for MIDI events'''
    bl_idname = 'MidiSocketType'
    bl_label = 'MIDI'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.9, 0.86, 0.14, 1.0)

classes.append(MidiSocket)

class TriggerOperator(Operator):
    '''One-off trigger'''
    bl_idname = 'audionodes.trigger'
    bl_label = "Trigger"

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'socket') and isinstance(context.socket, TriggerSocket)

    def invoke(self, context, event):
        context.node.send_value_update(context.socket.get_index(), 1)
        return {'FINISHED'}

classes.append(TriggerOperator)

class TriggerResetOperator(Operator):
    '''One-off trigger reset'''
    bl_idname = 'audionodes.trigger_reset'
    bl_label = "Reset"

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'socket') and isinstance(context.socket, TriggerSocket)

    def invoke(self, context, event):
        context.node.send_value_update(context.socket.get_index(), 2)
        return {'FINISHED'}

classes.append(TriggerResetOperator)

class TriggerSocket(NodeSocket, AudioTreeNodeSocket):
    '''Socket for trigger events'''
    bl_idname = 'TriggerSocketType'
    bl_label = 'Trigger'

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            row = layout.row(align=True)
            row.operator("audionodes.trigger", text=text)
            row.operator("audionodes.trigger_reset", text="", icon='FILE_REFRESH')

    def draw_color(self, context, node):
        return (0.52734375, 0.99609375, 0.87109375, 1.0)

classes.append(TriggerSocket)

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

