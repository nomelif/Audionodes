add_paths (NATIVE_SRCS
  audionodes.cpp
  node.cpp
  node_tree.cpp
  polyphony.cpp
)
add_paths (NATIVE_PUBLIC_HEADER c_interface.h)
add_paths (NATIVE_HEADERS .)

include (${CMAKE_CURRENT_LIST_DIR}/util/CMakeLists.txt)
include (${CMAKE_CURRENT_LIST_DIR}/data/CMakeLists.txt)
include (${CMAKE_CURRENT_LIST_DIR}/nodes/CMakeLists.txt)
