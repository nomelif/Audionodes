
import cffi, os

ffi = cffi.FFI()
ffi.cdef("void push(void * target, int value);")
ffi.cdef("void * allocate();")
ffi.cdef("void main_loop(void * queue);")

C = ffi.dlopen(os.path.join(os.path.dirname(__file__), "test.so"))

queue = C.allocate()

from threading import Thread

thread = Thread(target=C.main_loop, args=[queue]).start()

