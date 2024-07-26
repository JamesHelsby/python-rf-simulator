cmake_minimum_required(VERSION 3.10)
project(Assumption5)

set(CMAKE_CXX_STANDARD 17)

# Boost libraries
find_package(Boost REQUIRED COMPONENTS graph)
include_directories(${Boost_INCLUDE_DIRS})

# Other includes
include_directories(include)

add_executable(Assumption5 src/main.cpp)
target_link_libraries(Assumption5 ${Boost_LIBRARIES})
