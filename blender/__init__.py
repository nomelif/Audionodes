from . import ffi

classes = []

from . import node_tree, nodes, midi_in
for mod in (node_tree, nodes, midi_in):
    classes += mod.classes

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
