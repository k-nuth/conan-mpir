from conans.model.conan_file import ConanFile
from conans import CMake
import os

############### CONFIGURE THESE VALUES ##################
default_user = "bitprim"
default_channel = "stable"
#########################################################

channel = os.getenv("CONAN_CHANNEL", default_channel)
username = os.getenv("CONAN_USERNAME", default_user)

class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"
    requires = "mpir/6.1.2@%s/%s" % (username, channel)

    # def build(self):
    #     cmake = CMake(self.settings)
    #     self.run('cmake . %s' % cmake.command_line)
    #     self.run("cmake --build . %s" % cmake.build_config)

    def build(self):
        pass
        # cmake = CMake(self)
        # cmake.configure(source_dir="../../", build_dir="./")
        # cmake.build()

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")
        
    def test(self):
        pass
        # self.run(".%sbin%sexample %d" % (os.sep, os.sep, 1024))
