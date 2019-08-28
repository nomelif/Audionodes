# Blender addon sorcery

bl_info = {
    "name": "Audionodes",
    "description": "Create complex soundscapes in real time using nodes.",
    "author": "Roope Salmi, Théo Friberg",
    "version": (0,3,2),
    "blender": (2,80,0),
    "location": "Node Editor > Sound Icon > Add new",
    "warning": "Very much alpha, may blow up in your face.",
    "category": "Node",
    "tracker_url": "https://github.com/nomelif/Audionodes/issues",
    "wiki_url": "https://github.com/nomelif/Audionodes/wiki"
}

# Move all of this into blender/__init__.py?

import bpy
import time
from bpy.types import NodeTree, Node, NodeSocket, NodeSocketFloat

from struct import pack
from array import array

import threading

import wave
import struct
import tempfile
import platform

from . import blender
node_tree = blender.node_tree
ffi = blender.ffi

def register():
    blender.register()
    ffi.initialize()

def unregister():
    ffi.cleanup()
    blender.unregister()

import atexit
def exit_handler():
    ffi.cleanup()
atexit.register(exit_handler)

from bpy.app.handlers import persistent
@persistent
def pre_load_handler(_):
    ffi.flag_loading_file = True
    ffi.cleanup()

@persistent
def post_load_handler(_):
    ffi.initialize()
    ffi.flag_loading_file = False
    for tree in bpy.data.node_groups:
        if type(tree) == node_tree.AudioTree:
            tree.post_load_handler()

bpy.app.handlers.load_pre.append(pre_load_handler)
bpy.app.handlers.load_post.append(post_load_handler)

if __name__ == "__main__":
    register()
