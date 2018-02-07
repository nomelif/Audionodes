cmake_minimum_required (VERSION 3.9)
project (Audionodes LANGUAGES C CXX VERSION 0.2.1)
set (CMAKE_CXX_STANDARD 14)

# Helper function for adding source file paths to a list
function (add_paths to)
  set (to_tmp ${${to}})
  foreach (f ${ARGN})
    file (RELATIVE_PATH f_path ${CMAKE_SOURCE_DIR} "${CMAKE_CURRENT_LIST_DIR}/${f}")
    list (APPEND to_tmp "${f_path}")
  endforeach ()
  set (${to} "${to_tmp}" PARENT_SCOPE)
endfunction ()

# Native (backend) shared library
# Collect source files
include (native/CMakeLists.txt)

add_library (native SHARED ${NATIVE_SRCS})
set_target_properties (native PROPERTIES PUBLIC_HEADER ${NATIVE_PUBLIC_HEADER})
target_include_directories (native PRIVATE ${NATIVE_HEADERS})

# Dependencies
find_path (SDL2_INCLUDE_DIR SDL2/SDL.h)
find_library (SDL2_LIBRARY SDL2)
find_path (FLUID_INCLUDE_DIR NAMES fluidsynth.h)
find_library (FLUID_LIBRARY fluidsynth)
target_include_directories (native PRIVATE ${SDL2_INCLUDE_DIR})
target_include_directories (native PRIVATE ${FLUID_INCLUDE_DIR})
target_link_libraries (native ${SDL2_LIBRARY})
target_link_libraries (native ${FLUID_LIBRARY})    

# Make a .zip-file which can be installed into Blender
add_custom_target (blender 
  COMMAND ${CMAKE_COMMAND} -E make_directory Audionodes
  COMMAND ${CMAKE_COMMAND} -E copy
    $<TARGET_FILE_NAME:native>
    "${CMAKE_CURRENT_SOURCE_DIR}/__init__.py"
    Audionodes
  COMMAND ${CMAKE_COMMAND} -E make_directory Audionodes/blender
  COMMAND ${CMAKE_COMMAND} -E copy_directory
    "${CMAKE_CURRENT_SOURCE_DIR}/blender"
    Audionodes/blender
  COMMAND ${CMAKE_COMMAND} -E tar "cfv" "${CMAKE_PROJECT_NAME}.zip" --format=zip Audionodes
  COMMAND ${CMAKE_COMMAND} -E remove_directory Audionodes
)
add_dependencies (blender native)

find_program (BLENDER blender)
if (NOT BLENDER)
  message (WARNING "Blender executable not found, blender_install won't work.")
else ()
  # Install the addon directly into the found Blender installation
  message (STATUS "blender_install will use installation found at ${BLENDER}.")
  add_custom_target (blender_install COMMAND
    ${BLENDER} -b -P "${CMAKE_SOURCE_DIR}/blender_install.py" --
      install ${CMAKE_PROJECT_NAME}
      "${CMAKE_BINARY_DIR}/${CMAKE_PROJECT_NAME}.zip"
  )
  add_dependencies (blender_install blender)
  add_custom_target (blender_enable COMMAND
    ${BLENDER} -b -P "${CMAKE_SOURCE_DIR}/blender_install.py" --
      enable ${CMAKE_PROJECT_NAME}
  )
  add_custom_target (blender_uninstall COMMAND
    ${BLENDER} -b -P "${CMAKE_SOURCE_DIR}/blender_install.py" --
      uninstall ${CMAKE_PROJECT_NAME}
  )
endif ()
