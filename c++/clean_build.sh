#!/bin/bash

# Navigate to the correct directory
cd "$(dirname "$0")"

# Remove the build directory if it exists
if [ -d build ]; then
    rm -rf build
fi

# Create a new build directory
mkdir build
cd build

# Run CMake and Make
cmake ..
make
