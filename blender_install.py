# Installs or enables a Blender addon
# should be used via CMake
# Usage:
# blender -b -P blender_install.py -- install <addon name> <path>
# blender -b -P blender_install.py -- enable <addon name>
# blender -b -P blender_install.py -- uninstall <addon name>

print("""\033[94m
Note: Blender might print misleading error messages.
These can most likely be ignored if the target doesn't fail.
\033[0m""")

import bpy, sys
argv = sys.argv
argv = argv[argv.index("--") + 1:]
if argv[0] == "install":
    try:
        bpy.ops.wm.addon_disable(module=argv[1])
        bpy.ops.wm.addon_remove(module=argv[1])
    except:
        # Addon not previously installed, fine
        pass
    bpy.ops.wm.addon_install(filepath=argv[2])
elif argv[0] == "enable":
    bpy.ops.wm.addon_enable(module=argv[1])
    bpy.ops.wm.save_userpref()
elif argv[0] == "uninstall":
    try:
        bpy.ops.wm.addon_disable(module=argv[1])
        bpy.ops.wm.addon_remove(module=argv[1])
    except:
        pass
    bpy.ops.wm.save_userpref()

