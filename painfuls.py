import platform
import importlib
import sys
import os

def fix(modules = ("pygame", "numpy")):

    if platform.system() == "Windows":
        sys.path.append(os.getenv("APPDATA"))
        mod = importlib.import_module("ANPath")
        return mod.importAll(modules)
    else:

        result = []

        import numpy as np
        import pygame
        import pygame.midi

        for module in modules:
            if module == "pygame":
                result.append(pygame)
            elif module == "numpy":
                result.append(np)
            elif module == "pygame.midi":
                result.append(pygame.midi)
            
        return tuple(result)
