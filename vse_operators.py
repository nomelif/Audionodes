import bpy

alsa_ok = False

import time
from threading import Thread

from .painfuls import fix

pygame, np, midi = fix(("pygame", "numpy", "pygame.midi"))

class VSERecord(bpy.types.Operator):
    bl_idname = "audionodes.record"
    bl_label = "Record to sequencer"

    def execute(self, context):
        tree = context.active_node.getTree()
        tree.toggleRecording()
        return {'FINISHED'}
