from conans import ConanFile
import os, shutil
from conans.tools import download, unzip, replace_in_file, check_md5
from conans import CMake
from conans import tools
import subprocess
import shutil
import importlib


microarchitecture_default = 'x86_64'

def get_cpuid():
    try:
        cpuid = importlib.import_module('cpuid')
        return cpuid
    except ImportError:
        # print("*** cpuid could not be imported")
        return None

def get_cpu_microarchitecture_or_default(default):
    cpuid = get_cpuid()
    if cpuid != None:
        return '%s%s' % cpuid.cpu_microarchitecture()
    else:
        return default

def get_cpu_microarchitecture():
    return get_cpu_microarchitecture_or_default(microarchitecture_default)


class BitprimMpirConan(ConanFile):
    name = "mpir"
    version = "3.0.0"
    url = "https://github.com/bitprim/bitprim-conan-mpir"
    ZIP_FOLDER_NAME = "mpir-%s" % version
    
    # generators = "cmake"
    generators = "txt"

    settings =  "os", "compiler", "arch", "build_type"
    build_policy = "missing"

    options = {"shared": [True, False],
               "disable_assembly": [True, False],
               "enable_fat": [True, False],
               "enable_cxx": [True, False],
               "disable-fft": [True, False],
               "enable-assert": [True, False],
               "microarchitecture": "ANY" #["x86_64", "haswell", "ivybridge", "sandybridge", "bulldozer", ...]
               }

    default_options = "shared=False", "disable_assembly=False", "enable_fat=False", \
                      "enable_cxx=True", "disable-fft=False", "enable-assert=False", \
                      "microarchitecture=_DUMMY_"

    # requires = "m4/1.4.18@bitprim/stable"

    def _simplify_microarchitecture(self):

        # if self.options.microarchitecture in ['x86_64', 'athlon64', 'k8', 'core2', 'corei', 'coreinhm', 'coreiwsm', 'nehalem', 'westmere', 'coreisbr', 'coreisbrnoavx', 'coreiibr', 'coreiibrnoavx', 'sandybridge', 'sandybridgenoavx', 'ivybridge', 'ivybridgenoavx']:
        #     return 'core2'

        if self.options.microarchitecture in ['coreihwl', 'coreihwlnoavx', 'haswell', 'haswellnoavx', 'coreibwl', 'coreibwlnoavx', 'broadwell', 'broadwellnoavx',
                                              'bulldozer', 'bd1', 'bulldozernoavx', 'bd1noavx', 'piledriver', 'bd2', 'piledrivernoavx', 'bd2noavx', 'steamroller', 'bd3', 'steamrollernoavx', 'bd3noavx', 'excavator', 'bd4', 'excavatornoavx', 'bd4noavx']:
            return 'haswell'

        if self.options.microarchitecture in ['skylake', 'skylakenoavx', 'kabylake', 'kabylakenoavx']:
            return 'skylake'

        return 'core2'


    def configure(self):
        if self.options.microarchitecture == "_DUMMY_":
            self.options.microarchitecture = get_cpu_microarchitecture()
        self.output.info("Detected microarchitecture: %s" % (self.options.microarchitecture,))
        self.options.microarchitecture = self._simplify_microarchitecture()
        self.output.info("Compiling for microarchitecture: %s" % (self.options.microarchitecture,))

    def requirements(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc": #MinGW
            self.requires.add("m4/1.4.18@bitprim/stable")

    def source(self):
        # http://mpir.org/mpir-3.0.0.tar.bz2
        zip_name = "mpir-%s.tar.bz2" % self.version
        download("http://mpir.org/%s" % zip_name, zip_name)

        # check_md5(zip_name, "4c175f86e11eb32d8bf9872ca3a8e11d") #TODO
        unzip(zip_name)
        os.unlink(zip_name)

        yasm_version = '1.3.0'
        sys_arch = '64'
        yasm_site = 'http://www.tortall.net/projects/yasm/releases/'
        yasm_exe = 'yasm-%s-win%s.exe' % (yasm_version, sys_arch)
        yasm_download = '%s/%s' % (yasm_site, yasm_exe)
        self.output.warn("yasm_download: %s" % (yasm_download))
        
        download(yasm_download, 'yasm.exe')

        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            yasm_path = '%s\\' % (os.getcwd()) 
            os.environ['YASMPATH'] = yasm_path

            self.run("git clone https://github.com/ShiftMediaProject/VSYASM.git")
            shutil.copy('./VSYASM/yasm.props', './mpir-3.0.0/build.vc/vsyasm.props')
            shutil.copy('./VSYASM/yasm.targets', './mpir-3.0.0/build.vc/vsyasm.targets')
            shutil.copy('./VSYASM/yasm.xml', './mpir-3.0.0/build.vc/vsyasm.xml')
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
            # shutil.copy('./yasm.exe', 'C:/Windows/system32/yasm.exe')

            # for file in os.listdir("./"):
            #     if file.endswith("yasm.exe"):
            #         print(os.path.join("./", file))

            shutil.copy('./yasm.exe', 'C:/Windows/system32/')
            shutil.copy('./yasm.exe', 'C:/MinGw/bin/')

            # for file in os.listdir("C:/MinGw/bin/"):
            #     if file.endswith("yasm.exe"):
            #         print(os.path.join("C:/MinGw/bin/", file))


    def _generic_env_configure_vars(self, verbose=False):
        """Reusable in any lib with configure!!"""
        command = ""
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            libs = 'LIBS="%s"' % " ".join(["-l%s" % lib for lib in self.deps_cpp_info.libs])
            ldflags = 'LDFLAGS="%s"' % " ".join(["-L%s" % lib for lib in self.deps_cpp_info.lib_paths])
            archflag = "-m32" if self.settings.arch == "x86" else ""
            cflags = 'CFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cflags))
            cpp_flags = 'CPPFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cppflags))
            command = "env %s %s %s %s" % (libs, ldflags, cflags, cpp_flags)
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            cl_args = " ".join(['/I"%s"' % lib for lib in self.deps_cpp_info.include_paths])
            lib_paths= ";".join(['"%s"' % lib for lib in self.deps_cpp_info.lib_paths])
            command = "SET LIB=%s;%%LIB%% && SET CL=%s" % (lib_paths, cl_args)
            if verbose:
                command += " && SET LINK=/VERBOSE"
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            libs = 'LIBS="%s"' % " ".join(["-l%s" % lib for lib in self.deps_cpp_info.libs])
            ldflags = 'LDFLAGS="%s"' % " ".join(["-L%s" % lib for lib in self.deps_cpp_info.lib_paths])
            archflag = "-m32" if self.settings.arch == "x86" else ""
            cflags = 'CFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cflags))
            cpp_flags = 'CPPFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cppflags))
            command = "env %s %s %s %s" % (libs, ldflags, cflags, cpp_flags)

        return command

    def _determine_host(self):
        if self.settings.os == "Macos":
            # nehalem-apple-darwin15.6.0
            os_part = 'apple-darwin'
        elif self.settings.os == "Linux":
            os_part = 'pc-linux-gnu'
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc": #MinGW
            os_part = 'pc-msys'

        complete_host = "%s-%s" % (self.options.microarchitecture, os_part)
        host_string = " --build=%s --host=%s" % (complete_host, complete_host)
        return host_string


    # def _msvc_microarchitecture(self):
    #     # if self.options.microarchitecture in ['x86_64', 'athlon64', 'k8', 'core2', 'corei', 'coreinhm', 'coreiwsm', 'nehalem', 'westmere', 'coreisbr', 'coreisbrnoavx', 'coreiibr', 'coreiibrnoavx', 'sandybridge', 'sandybridgenoavx', 'ivybridge', 'ivybridgenoavx']:
    #     #     return 'core2'
    #     if self.options.microarchitecture in ['coreihwl', 'coreihwlnoavx', 'haswell', 'haswellnoavx', 'coreibwl', 'coreibwlnoavx', 'broadwell', 'broadwellnoavx',
    #                                           'bulldozer', 'bd1', 'bulldozernoavx', 'bd1noavx', 'piledriver', 'bd2', 'piledrivernoavx', 'bd2noavx', 'steamroller', 'bd3', 'steamrollernoavx', 'bd3noavx', 'excavator', 'bd4', 'excavatornoavx', 'bd4noavx']:
    #         return 'haswell_avx'
    #     if self.options.microarchitecture in ['skylake', 'skylakenoavx', 'kabylake', 'kabylakenoavx']:
    #         return 'skylake_avx'
    #     return 'core2'
   
    def _msvc_microarchitecture(self):
        if self.options.microarchitecture in ['haswell']:
            return 'haswell_avx'

        if self.options.microarchitecture in ['skylake']:
            return 'skylake_avx'

        return 'core2'

    def build(self):
        self.output.warn("*** Detected OS: %s" % (self.settings.os))

        if self.settings.compiler == "Visual Studio":
            self.output.warn("*** Detected Visual Studio version: %s" % (self.settings.compiler.version))

        yasm_path = '%s\\' % (os.getcwd()) 
        os.environ['YASMPATH'] = yasm_path

        if not os.path.exists('C:/Bitprim/usr/bin'):
            shutil.copytree('C:/Program Files/Git/usr/bin', 'C:/Bitprim/usr/bin')

        os.environ['PATH'] += os.pathsep + yasm_path
        os.environ['PATH'] = 'C:/Bitprim/usr/bin' + os.pathsep + os.environ['PATH']
        # self.output.warn("*** PATH: %s" % (os.environ['PATH']))

        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            if self.settings.compiler.version == 14:
                build_dir = 'build.vc14'
            elif  self.settings.compiler.version == 15:
                build_dir = 'build.vc15'

            build_path = os.path.join(self.ZIP_FOLDER_NAME, build_dir)
            self.output.warn("*** Detected build_path:   %s" % (build_path))

            with tools.chdir(build_path):
                # self.run("msbuild.bat haswell_avx lib x64 release")
                self.run("msbuild.bat %s lib x64 release" % (self._msvc_microarchitecture(),))

        # elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
        else:
            old_path = os.environ['PATH']
            os.environ['PATH'] += os.pathsep + os.getcwd()

            os.environ['MAKE'] = 'mingw32-make'
            # # os.environ['SHELL'] = '"C:/Program Files/Git/usr/bin/sh.exe"'
            # os.environ['SHELL'] = 'pepe.exe'
            config_options_string = ""

            for option_name in self.options.values.fields:
                if option_name != 'microarchitecture':
                    activated = getattr(self.options, option_name)
                    if activated:
                        self.output.info("Activated option! %s" % option_name)
                        config_options_string += " --%s" % option_name.replace("_", "-")

            self.output.warn("*** Detected OS: %s" % (self.settings.os))

            if self.settings.os == "Macos":
                config_options_string += " --with-pic"

            host_string = self._determine_host()
            self.output.warn(host_string)

            disable_assembly = "--disable-assembly" if self.settings.arch == "x86" else ""

            configure_command = "cd %s && %s ./configure %s --with-pic --enable-static --enable-shared %s %s" % (self.ZIP_FOLDER_NAME, self._generic_env_configure_vars(), host_string, config_options_string, disable_assembly)
            self.output.warn("*** configure_command: %s" % (configure_command))
            self.run(configure_command)

            if self.settings.os != "Windows":
                self.run("cd %s && make" % self.ZIP_FOLDER_NAME)
            else:
                self.run("cd %s && mingw32-make MAKE=mingw32-make" % self.ZIP_FOLDER_NAME)
            os.environ['PATH'] = old_path


    def imports(self):
        self.copy("m4", dst=".", src="bin")
        self.copy("m4.exe", dst=".", src="bin")
        self.copy("regex2.dll", dst=".", src="bin")

    def package(self):

        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            src_inc_dir = '%s'  % (self.ZIP_FOLDER_NAME)
            dst_inc_dir = '%s/.includes'  % (self.ZIP_FOLDER_NAME)
            lib_dir = '%s/.libs'  % (self.ZIP_FOLDER_NAME)
            self.output.warn("lib_dir: %s" % (lib_dir))

            if not os.path.exists(dst_inc_dir):
                os.makedirs(dst_inc_dir)

            shutil.copy('%s/mpir.h'  % (src_inc_dir), '%s/gmp.h'  % (dst_inc_dir))
            shutil.copy('%s/mpirxx.h'  % (src_inc_dir), '%s/gmpxx.h'  % (dst_inc_dir))

            shutil.copy('%s/mpir.h'  % (src_inc_dir), '%s/'  % (dst_inc_dir))
            shutil.copy('%s/mpirxx.h'  % (src_inc_dir), '%s/'  % (dst_inc_dir))
            shutil.copy('%s/config.h'  % (src_inc_dir), '%s/'  % (dst_inc_dir))
            shutil.copy('%s/gmp-impl.h'  % (src_inc_dir), '%s/'  % (dst_inc_dir))
            shutil.copy('%s/gmp-mparam.h'  % (src_inc_dir), '%s/'  % (dst_inc_dir))
            shutil.copy('%s/longlong.h'  % (src_inc_dir), '%s/'  % (dst_inc_dir))
            shutil.copy('%s/longlong_post.h'  % (src_inc_dir), '%s/'  % (dst_inc_dir))
            shutil.copy('%s/longlong_pre.h'  % (src_inc_dir), '%s/'  % (dst_inc_dir))
            shutil.copy('%s/randmt.h'  % (src_inc_dir), '%s/'  % (dst_inc_dir))

            self.copy("*.h", dst="include", src=dst_inc_dir, keep_path=False)
            # self.copy("*.h", dst="include", src=src_inc_dir, keep_path=True)
            # self.copy(pattern="*.so*", dst="lib", src=lib_dir, keep_path=False)
            self.copy(pattern="*.a", dst="lib", src=lib_dir, keep_path=False)
            self.copy(pattern="*.la", dst="lib", src=lib_dir, keep_path=False)

        else:
            lib_dir = '%s/lib/x64/Release'  % (self.ZIP_FOLDER_NAME)
            self.output.warn("lib_dir: %s" % (lib_dir))
            self.copy("*.h", dst="include", src=lib_dir, keep_path=True)
            self.copy(pattern="*.dll*", dst="bin", src=lib_dir, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=lib_dir, keep_path=False)
        
    def package_info(self):
        # self.output.warn("*** self.cpp_info.libs:   %s" % (self.cpp_info.libs))
        self.cpp_info.libs = ['mpir']
        # self.output.warn("*** self.cpp_info.libs:   %s" % (self.cpp_info.libs))




    # def config(self):
    #     pass
    #     # del self.settings.compiler.libcxx




        # Core2
        # Nehalem           |   Westmere                        || 
        # Sandy Bridge      |   Ivy Bridge  (F16C, RdRand)      || 
        # Haswell           |   Broadwell   (?)
        # Skylake

        # K8 Hammer (first 64 bit)
        # K10
        # bulldozer
        # Piledriver
        # Steamroller
        # Excavator
        # Zen
        # Zen 2
        # Zen 3

        # Faltan los low-power/low-cost markets: por ejemplo: Bobcat (AMD), Jaguar (AMD), Puma (AMD), 

        # lib_mpir_cxx
        # lib_mpir_gc
        # lib_mpir_p3
        # lib_mpir_core2
        # lib_mpir_haswell_avx
        # lib_mpir_skylake_avx

