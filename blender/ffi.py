
import os
import ctypes as ct
import platform

native_fname = {
    "Linux": "libnative.so",
    "Darwin": "libnative.dylib",
    "Windows": "bin\\native.dll"
}[platform.system()]
native_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", native_fname))
if not os.path.isfile(native_path):
    raise AssertionError("""Audionodes: Unable to locate the native backend shared library.
Expected to find it at %s.
NOTE: The addon will not work if you download a raw repository-zip, \
because the native backend needs to be compiled.
Please make sure you download the addon from the Releases-page or compile the backend yourself.""" % native_path)

if os.name == 'nt':
    # Source: https://stackoverflow.com/a/7586821
    from ctypes import wintypes
    LOAD_WITH_ALTERED_SEARCH_PATH = 0x00000008
    kernel32 = ct.WinDLL("kernel32", use_last_error=True)
    def check_bool(result, func, args):
        if not result:
            raise ct.WinError(ct.get_last_error())
        return args

    kernel32.LoadLibraryExW.errcheck = check_bool
    kernel32.LoadLibraryExW.restype = wintypes.HMODULE
    kernel32.LoadLibraryExW.argtypes = (wintypes.LPCWSTR, wintypes.HANDLE, wintypes.DWORD)

if os.name == 'nt':
    handle = kernel32.LoadLibraryExW(native_path, None, LOAD_WITH_ALTERED_SEARCH_PATH)
    native = ct.CDLL(native_path, mode=0, handle=handle)
else:
    # mode=8 stands for RTLD_DEEPBIND dlopen flag [DISABLED]
    native = ct.CDLL(native_path, mode=0)

flag_loading_file = False
flag_initialized = False

native.audionodes_initialize.argtypes = []
native.audionodes_initialize.restype = None
def initialize():
    global flag_initialized
    if not flag_initialized:
        native.audionodes_initialize()
        flag_initialized = True

native.audionodes_cleanup.argtypes = []
native.audionodes_cleanup.restype = None
def cleanup():
    global flag_initialized
    if flag_initialized:
        native.audionodes_cleanup()
        flag_initialized = False

native.audionodes_create_node.argtypes = [ct.c_char_p]
native.audionodes_create_node.restype = ct.c_int
def create_node(node_type):
    return native.audionodes_create_node(node_type)

native.audionodes_copy_node.argtypes = [ct.c_int, ct.c_char_p]
native.audionodes_copy_node.restype = ct.c_int
def copy_node(old_id, node_type):
    return native.audionodes_copy_node(old_id, node_type)

native.audionodes_remove_node.argtypes = [ct.c_int]
native.audionodes_remove_node.restype = None
def remove_node(node_id):
    native.audionodes_remove_node(node_id)
    
native.audionodes_node_exists.argtypes = [ct.c_int]
native.audionodes_node_exists.restype = ct.c_bool
def node_exists(node_id):
    return native.audionodes_node_exists(node_id)

native.audionodes_update_node_input_value.argtypes = [ct.c_int, ct.c_int, ct.c_float]
native.audionodes_update_node_input_value.restype = None
def update_node_input_value(node_id, socket_id, val):
    native.audionodes_update_node_input_value(node_id, socket_id, val)

native.audionodes_update_node_property_value.argtypes = [ct.c_int, ct.c_int, ct.c_int]
native.audionodes_update_node_property_value.restype = None
def update_node_property_value(node_id, socket_id, val):
    native.audionodes_update_node_property_value(node_id, socket_id, int(val))

native.audionodes_send_node_binary_data.argtypes = [ct.c_int, ct.c_int, ct.c_int, ct.c_char_p]
native.audionodes_send_node_binary_data.restype = None
def send_node_binary_data(node_id, slot, data):
    native.audionodes_send_node_binary_data(node_id, slot, len(data), data)

native.audionodes_begin_tree_update.argtypes = []
native.audionodes_begin_tree_update.restype = ct.c_void_p
def begin_tree_update():
    return native.audionodes_begin_tree_update()

native.audionodes_add_tree_update_link.argtypes = [ct.c_void_p, ct.c_int, ct.c_int, ct.c_size_t, ct.c_size_t]
native.audionodes_add_tree_update_link.restype = None
def add_tree_update_link(ref, from_node, to_node, from_socket, to_socket):
    native.audionodes_add_tree_update_link(ref, from_node, to_node, from_socket, to_socket)

native.audionodes_finish_tree_update.argtypes = [ct.c_void_p]
native.audionodes_finish_tree_update.restype = None
def finish_tree_update(ref):
    native.audionodes_finish_tree_update(ref)
