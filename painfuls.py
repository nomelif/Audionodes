import platform
import importlib
import sys
import os

def fix():

    if platform.system() == "Windows":
        sys.path.append(os.getenv("APPDATA"))
        mod = importlib.import_module("ANPath")
        return mod.importAll()
    else:
        import numpy as np
        import pygame
        return pygame, np
