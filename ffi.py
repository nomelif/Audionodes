
import cffi, os

ffi = cffi.FFI()

with open(os.path.join(os.path.dirname(__file__), "native/c_interface.h"), 'r') as file:
    interface = file.read()
    ffi.cdef(interface)

native = ffi.dlopen(os.path.join(os.path.dirname(__file__), "native.so"), ffi.RTLD_DEEPBIND)

flag_loading_file = False
flag_initialized = False

def initialize():
    global flag_initialized
    if not flag_initialized:
        native.initialize()
        flag_initialized = True

def cleanup():
    global flag_initialized
    if flag_initialized:
        native.cleanup()
        flag_initialized = False
