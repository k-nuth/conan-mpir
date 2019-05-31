[![Build Status](https://travis-ci.org/k-nuth/kth-conan-mpir.svg?branch=master)](https://travis-ci.org/k-nuth/kth-conan-mpir) [![Appveyor Status](https://ci.appveyor.com/api/projects/status/github/k-nuth/kth-conan-mpir?branch=master&svg=true)](https://ci.appveyor.com/project/k-nuth/kth-conan-mpir?branch=master)

# kth-conan-mpir

[Conan.io](https://conan.io) package for GMP library. https://gmplib.org/

The packages generated with this **conanfile** can be found in [conan.io](https://conan.io/source/gmp/3.0.0/k-nuth/k-nuth).

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py
    
## Upload packages to server

    $ conan upload mpir/3.0.0@kth/stable --all
    
## Reuse the packages

### Basic setup

    $ conan install mpir/3.0.0@kth/stable
    
### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    mpir/3.0.0@kth/stable

    [options]
    mpir:shared=false # true
    
    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install . 

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.
