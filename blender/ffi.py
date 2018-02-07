
import os
import ctypes as ct

native_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "libnative.so"))
# mode=8 stands for RTLD_DEEPBIND dlopen flag
native = ct.CDLL(native_path, mode=8)

flag_loading_file = False
flag_initialized = False

native.initialize.argtypes = []
native.initialize.restype = None
def initialize():
    global flag_initialized
    if not flag_initialized:
        native.initialize()
        flag_initialized = True

native.cleanup.argtypes = []
native.cleanup.restype = None
def cleanup():
    global flag_initialized
    if flag_initialized:
        native.cleanup()
        flag_initialized = False

native.create_node.argtypes = [ct.c_char_p]
native.create_node.restype = ct.c_int
def create_node(node_type):
    return native.create_node(node_type)

native.copy_node.argtypes = [ct.c_int, ct.c_char_p]
native.copy_node.restype = ct.c_int
def copy_node(old_id, node_type):
    return native.copy_node(old_id, node_type)

native.remove_node.argtypes = [ct.c_int]
native.remove_node.restype = None
def remove_node(node_id):
    native.remove_node(node_id)
    
native.node_exists.argtypes = [ct.c_int]
native.node_exists.restype = ct.c_bool
def node_exists(node_id):
    return native.node_exists(node_id)

native.update_node_input_value.argtypes = [ct.c_int, ct.c_int, ct.c_float]
native.update_node_input_value.restype = None
def update_node_input_value(node_id, socket_id, val):
    native.update_node_input_value(node_id, socket_id, val)

native.update_node_property_value.argtypes = [ct.c_int, ct.c_int, ct.c_int]
native.update_node_property_value.restype = None
def update_node_property_value(node_id, socket_id, val):
    native.update_node_property_value(node_id, socket_id, val)

native.begin_tree_update.argtypes = []
native.begin_tree_update.restype = ct.c_void_p
def begin_tree_update():
    return native.begin_tree_update()

native.add_tree_update_link.argtypes = [ct.c_void_p, ct.c_int, ct.c_int, ct.c_size_t, ct.c_size_t]
native.add_tree_update_link.restype = None
def add_tree_update_link(ref, from_node, to_node, from_socket, to_socket):
    native.add_tree_update_link(ref, from_node, to_node, from_socket, to_socket)

native.finish_tree_update.argtypes = [ct.c_void_p]
native.finish_tree_update.restype = None
def finish_tree_update(ref):
    native.finish_tree_update(ref)
