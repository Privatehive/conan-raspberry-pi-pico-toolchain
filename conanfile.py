#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.system.package_manager import Apt, PacMan
from conan.tools.files import download, get, unzip, copy
from conan.errors import ConanInvalidConfiguration
import json, os

required_conan_version = ">=2.0"

class RaspberryPiPicoToolchainConan(ConanFile):

    jsonInfo = json.load(open("info.json", 'r'))
    # ---Package reference---
    name = jsonInfo["projectName"]
    version = jsonInfo["version"]
    user = jsonInfo["domain"]
    channel = "stable"
    # ---Metadata---
    description = jsonInfo["projectDescription"]
    license = jsonInfo["license"]
    author = jsonInfo["vendor"]
    topics = jsonInfo["topics"]
    homepage = jsonInfo["homepage"]
    url = jsonInfo["repository"]
    # ---Requirements---
    requires = []
    tool_requires = []
    # ---Sources---
    exports = ("info.json")
    exports_sources = ["Toolchain-rpi.cmake"]
    # ---Binary model---
    settings = "os", "arch"
    # ---Build---
    generators = []
    # ---Folders---
    no_copy_source = True

    def validate(self):
        valid_os = ["Linux"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} is only supported for the following operating systems: {valid_os}")
        valid_arch = ["x86_64"]
        if str(self.settings.arch) not in valid_arch:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} is only supported for the following architectures on {self.settings.os}: {valid_arch}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        #self.run("chmod -R +w " + os.path.join(self.source_folder, "x-tools"))
        #for val in self.conan_data["packages-" + self.version]:
        #    self.install_deb_pkg(val["name"], val["sha256"])

    def package(self):
        copy(self, pattern="*", src=self.source_folder, dst=self.package_folder)
        #copy(self, pattern="pico_sdk_init.cmake", src=self.source_folder, dst=self.package_folder)
        #copy(self, pattern="pico_sdk_version.cmake", src=self.source_folder, dst=self.package_folder)
        #copy(self, pattern="*", src=os.path.join(self.source_folder, "cmake"), dst=os.path.join(self.package_folder, "cmake"))
        #copy(self, pattern="*", src=os.path.join(self.source_folder, "sysroot", "lib"), dst=os.path.join(self.package_folder, "x-tools", self.toolchainabi, self.toolchainabi, "sysroot", "lib"))
        #copy(self, pattern="*", src=os.path.join(self.source_folder, "sysroot", "usr"), dst=os.path.join(self.package_folder, "x-tools", self.toolchainabi, self.toolchainabi, "sysroot", "usr"))

    def define_tool_var(self, name, value, bin_folder):
        path = os.path.join(bin_folder, value)
        self.output.info('Creating %s environment variable: %s' % (name, path))
        return path

    def package_info(self):
        package = self.package_folder

        #toolchain = os.path.join(package, 'x-tools', self.toolchainabi)
        #sysroot = os.path.join(toolchain, self.toolchainabi, 'sysroot')

        cmake_toolchain = os.path.join(package, 'pico_sdk_init.cmake')
        #toolchain_bin = os.path.join(toolchain, 'bin')

        #self.output.info('Creating CHOST environment variable: %s' % self.toolchainabi)
        #self.buildenv_info.define("CHOST", self.toolchainabi)

        #self.output.info('Appending PATH environment variable: %s' % toolchain_bin)
        #self.buildenv_info.append_path("PATH", toolchain_bin)

        self.output.info('Injecting cmaketoolchain:user_toolchain: %s' % cmake_toolchain)
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", cmake_toolchain)

        #self.buildenv_info.define_path("PKG_CONFIG_DIR", "")
        #self.buildenv_info.define_path("PKG_CONFIG_PATH", "")
        #self.buildenv_info.define_path("PKG_CONFIG_LIBDIR", os.path.os.path.join(sysroot, "usr", "lib", "arm-linux-gnueabihf", "pkgconfig"))
        #self.buildenv_info.append_path("PKG_CONFIG_LIBDIR", os.path.os.path.join(sysroot, "usr", "share", "pkgconfig"))
        #self.buildenv_info.define_path("PKG_CONFIG_SYSROOT_DIR", sysroot)

        #self.buildenv_info.define("CC", self.define_tool_var('CC', self.toolchainabi + '-gcc', toolchain_bin))
        #self.buildenv_info.define("CXX", self.define_tool_var('CXX', self.toolchainabi + '-g++', toolchain_bin))
        #self.buildenv_info.define("AS", self.define_tool_var('AS', self.toolchainabi + '-as', toolchain_bin))
        #self.buildenv_info.define("LD", self.define_tool_var('LD', self.toolchainabi + '-ld', toolchain_bin))
        #self.buildenv_info.define("AR", self.define_tool_var('AR', self.toolchainabi + '-ar', toolchain_bin))
        #self.buildenv_info.define("RANLIB", self.define_tool_var('RANLIB', self.toolchainabi + '-ranlib', toolchain_bin))
        #self.buildenv_info.define("STRIP", self.define_tool_var('STRIP', self.toolchainabi + '-strip', toolchain_bin))
        #self.buildenv_info.define("NM", self.define_tool_var('NM', self.toolchainabi + '-nm', toolchain_bin))
        #self.buildenv_info.define("ADDR2LINE", self.define_tool_var('ADDR2LINE', self.toolchainabi + '-addr2line', toolchain_bin))
        #self.buildenv_info.define("OBJCOPY", self.define_tool_var('OBJCOPY', self.toolchainabi + '-objcopy', toolchain_bin))
        #self.buildenv_info.define("OBJDUMP", self.define_tool_var('OBJDUMP', self.toolchainabi + '-objdump', toolchain_bin))
        #self.buildenv_info.define("READELF", self.define_tool_var('READELF', self.toolchainabi + '-readelf', toolchain_bin))
        #self.buildenv_info.define("ELFEDIT", self.define_tool_var('ELFEDIT', self.toolchainabi + '-elfedit', toolchain_bin))

        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
