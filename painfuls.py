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
        import numpy as np
        import pygame
        return pygame, np
