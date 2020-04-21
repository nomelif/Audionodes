
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

class CONFIGURATION_DESCRIPTOR(ct.Structure):
    _fields_ = [("field_populated", ct.c_bool),
                ("name", ct.c_char_p),
                ("current_value", ct.c_char_p),
                ("available_values", ct.POINTER(ct.c_char_p))]
native.audionodes_get_configuration_options.argtypes = [ct.c_int]
native.audionodes_get_configuration_options.restype = ct.POINTER(CONFIGURATION_DESCRIPTOR)
def get_configuration_options(node_id):
    opts = []
    ptr = native.audionodes_get_configuration_options(node_id)
    i = 0
    while ptr[i].field_populated:
        opt = (ptr[i].name.decode("utf8"), ptr[i].current_value.decode("utf8"), [])
        vals_ptr = ptr[i].available_values
        j = 0
        while vals_ptr[j]:
            opt[2].append(vals_ptr[j].decode("utf8"))
            j += 1
        opts.append(opt)
        i += 1
    return opts

native.audionodes_set_configuration_option.argtypes = [ct.c_int, ct.c_char_p, ct.c_char_p]
native.audionodes_set_configuration_option.restype = ct.c_int
def set_configuration_option(node_id, name, val):
    return native.audionodes_set_configuration_option(node_id,
        name.encode("utf8"), val.encode("utf8"))

class RETURN_MESSAGE_PAYLOAD(ct.Union):
    _fields_ = [
                ("integer", ct.c_int),   # 0
                ("number", ct.c_float),  # 1
                ("string", ct.c_char_p), # 2
               ]
class RETURN_MESSAGE(ct.Structure):
    _fields_ = [("field_populated", ct.c_bool),
                ("node_id", ct.c_int),
                ("msg_type", ct.c_int),
                ("data_type", ct.c_int),
                ("payload", RETURN_MESSAGE_PAYLOAD)]
    _anonymous_ = ("payload",)

native.audionodes_fetch_messages.argtypes = []
native.audionodes_fetch_messages.restype = ct.POINTER(RETURN_MESSAGE)
def fetch_messages():
    msgs = []
    ptr = native.audionodes_fetch_messages()
    i = 0
    while ptr[i].field_populated:
        payload = None
        if ptr[i].data_type == 0:
            payload = ptr[i].integer
        elif ptr[i].data_type == 1:
            payload = ptr[i].number
        elif ptr[i].data_type == 2:
            payload = ptr[i].string.decode("utf8")
        msgs.append((ptr[i].node_id, ptr[i].msg_type, payload))
        i += 1
    return msgs

native.audionodes_begin_tree_update.argtypes = []
native.audionodes_begin_tree_update.restype = None
def begin_tree_update():
    native.audionodes_begin_tree_update()

native.audionodes_add_tree_update_link.argtypes = [ct.c_int, ct.c_int, ct.c_size_t, ct.c_size_t]
native.audionodes_add_tree_update_link.restype = None
def add_tree_update_link(from_node, to_node, from_socket, to_socket):
    native.audionodes_add_tree_update_link(from_node, to_node, from_socket, to_socket)

native.audionodes_finish_tree_update.argtypes = []
native.audionodes_finish_tree_update.restype = None
def finish_tree_update():
    native.audionodes_finish_tree_update()
