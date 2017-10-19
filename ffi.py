
import cffi, os

ffi = cffi.FFI()
ffi.cdef("void initialize();")
ffi.cdef("void cleanup();")
ffi.cdef("int create_node(int type);")
ffi.cdef("int copy_node(intptr_t old_id, int type);")
ffi.cdef("void remove_node(intptr_t id);")
ffi.cdef("void update_node_input_value(intptr_t id, int input_index, float value);")
ffi.cdef("void* begin_tree_update();")
ffi.cdef("void add_tree_update_link(void *links, intptr_t from_node, intptr_t to_node, size_t from_socket, size_t to_socket);")
ffi.cdef("void finish_tree_update(void *links);")

native = ffi.dlopen(os.path.join(os.path.dirname(__file__), "native.so"))

