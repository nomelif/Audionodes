import bpy
import json

class FileOperations(bpy.types.Panel):

    """This panel shows the anode load operators."""

    bl_label = "Save and load audionodes"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "File"

    def draw(self, context):

        col = self.layout.column(align=True)
        col.operator("anode.save", text="Save", icon="SAVE_AS")
        col.operator("anode.load", text="Open", icon="FILE_FOLDER")

class NodesSave(bpy.types.Operator):

    """This operator serializes the nodes of the current tree to a file."""

    bl_idname = "anode.save"
    bl_label = "Save audionodes"
    bl_options = {"REGISTER"}


    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty()
    directory = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        tree = context.space_data.node_tree
        result = [node.serialize() for node in tree.nodes]
        text = json.dumps(result)
        try:
            with open(self.filepath, "w+") as f:
                f.write(text)
        except IOError:
            pass
        return {"FINISHED"}

    def invoke(self, context, event):

        self.filename = ""
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

class NodesLoad(bpy.types.Operator):

    """This operator deserializes the nodes from a file into the curren tree."""

    bl_idname = "anode.load"
    bl_label = "Load audionodes"
    bl_options = {"REGISTER"}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty()
    directory = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        tree = context.space_data.node_tree
        try:
            with open(self.filepath, "r") as f:
                text = f.read()
            nodes = []
            loaded_data = json.loads(text)
            for node in loaded_data:
                new_node = tree.nodes.new(node["type"])
                new_node.inflate(node)
                nodes.append(new_node)

            links = tree.links
            for node, data in zip(nodes, loaded_data):
                for i, input_data in enumerate(data["inputs"]):
                    if len(input_data["links"]) != 0:
                        link = input_data["links"][0]
                        links.new(tree.nodes[link["from_node"]].outputs[link["from_socket"]], node.inputs[i])



        except IOError:
            pass
        return {"FINISHED"}

    def invoke(self, context, event):

        self.filename = ""
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
