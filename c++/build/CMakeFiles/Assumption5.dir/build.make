# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.22

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /homes/jjh17/udp/udp-p2p/python/c++

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /homes/jjh17/udp/udp-p2p/python/c++/build

# Include any dependencies generated for this target.
include CMakeFiles/Assumption5.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/Assumption5.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/Assumption5.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/Assumption5.dir/flags.make

CMakeFiles/Assumption5.dir/src/main.cpp.o: CMakeFiles/Assumption5.dir/flags.make
CMakeFiles/Assumption5.dir/src/main.cpp.o: ../src/main.cpp
CMakeFiles/Assumption5.dir/src/main.cpp.o: CMakeFiles/Assumption5.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/homes/jjh17/udp/udp-p2p/python/c++/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/Assumption5.dir/src/main.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/Assumption5.dir/src/main.cpp.o -MF CMakeFiles/Assumption5.dir/src/main.cpp.o.d -o CMakeFiles/Assumption5.dir/src/main.cpp.o -c /homes/jjh17/udp/udp-p2p/python/c++/src/main.cpp

CMakeFiles/Assumption5.dir/src/main.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/Assumption5.dir/src/main.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /homes/jjh17/udp/udp-p2p/python/c++/src/main.cpp > CMakeFiles/Assumption5.dir/src/main.cpp.i

CMakeFiles/Assumption5.dir/src/main.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/Assumption5.dir/src/main.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /homes/jjh17/udp/udp-p2p/python/c++/src/main.cpp -o CMakeFiles/Assumption5.dir/src/main.cpp.s

# Object files for target Assumption5
Assumption5_OBJECTS = \
"CMakeFiles/Assumption5.dir/src/main.cpp.o"

# External object files for target Assumption5
Assumption5_EXTERNAL_OBJECTS =

Assumption5: CMakeFiles/Assumption5.dir/src/main.cpp.o
Assumption5: CMakeFiles/Assumption5.dir/build.make
Assumption5: /usr/lib/x86_64-linux-gnu/libboost_graph.so.1.74.0
Assumption5: /usr/lib/x86_64-linux-gnu/libboost_regex.so.1.74.0
Assumption5: CMakeFiles/Assumption5.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/homes/jjh17/udp/udp-p2p/python/c++/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable Assumption5"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/Assumption5.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/Assumption5.dir/build: Assumption5
.PHONY : CMakeFiles/Assumption5.dir/build

CMakeFiles/Assumption5.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/Assumption5.dir/cmake_clean.cmake
.PHONY : CMakeFiles/Assumption5.dir/clean

CMakeFiles/Assumption5.dir/depend:
	cd /homes/jjh17/udp/udp-p2p/python/c++/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /homes/jjh17/udp/udp-p2p/python/c++ /homes/jjh17/udp/udp-p2p/python/c++ /homes/jjh17/udp/udp-p2p/python/c++/build /homes/jjh17/udp/udp-p2p/python/c++/build /homes/jjh17/udp/udp-p2p/python/c++/build/CMakeFiles/Assumption5.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/Assumption5.dir/depend

