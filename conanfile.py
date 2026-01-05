#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.system.package_manager import Apt, PacMan
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.env import VirtualBuildEnv
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
    tool_requires = ["cmake/[>=3.13 <3.27]", "ninja/[>=1.11.1]"]
    # ---Sources---
    exports = ("info.json")
    exports_sources = ["Toolchain-rpi.cmake"]
    # ---Binary model---
    settings = "os", "compiler", "build_type", "arch"
    options = {"board": ["pico", "pico2"]}
    default_options = {"board": "pico"}
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

    def system_requirements(self):
        Apt(self).install(["binutils"])
        PacMan(self).install(["binutils"])

    def generate(self):
        ms = VirtualBuildEnv(self)
        tc = CMakeToolchain(self, generator="Ninja")
        tc.variables["PICO_SDK_PATH"] = os.path.join(self.source_folder, "pico-sdk-%s" % self.version)
        tc.generate()
        ms.generate()

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/raspberrypi/pico-sdk.git", target="pico-sdk-%s" % self.version, args=["--branch %s" % self.version, "--recursive", "--depth 1"])
        get(self, **self.conan_data["sources"]["picotool"][self.version])
        get(self, **self.conan_data["sources"]["arm-cross-compiler-pico"]["1.1.0"])
        get(self, **self.conan_data["sources"]["arm-cross-compiler-pico2"]["1.1.0"])
        self.run("chmod -R +w " + os.path.join(self.source_folder, "x-tools"))
        with open(os.path.join(self.source_folder, "x-tools", "arm-pico-eabi", "arm-pico-eabi.toolchain.cmake"), "r+", encoding="utf-8") as f:
            lines = f.readlines()
            f.seek(0)
            f.write("set(PICO_BOARD pico)")
            f.writelines(lines)
        with open(os.path.join(self.source_folder, "x-tools", "arm-pico2-eabi", "arm-pico2-eabi.toolchain.cmake"), "r+", encoding="utf-8") as f:
            lines = f.readlines()
            f.seek(0)
            f.write("set(PICO_BOARD pico2)")
            f.writelines(lines)

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="picotool-%s" % self.version)
        cmake.build()
        cmake.install()

    def package(self):
        copy(self, pattern="*", src=os.path.join(self.source_folder, "pico-sdk-%s" % self.version), dst=os.path.join(self.package_folder, "pico-sdk-%s" % self.version))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "x-tools"), dst=os.path.join(self.package_folder, "x-tools"))

    def define_tool_var(self, name, value, bin_folder):
        path = os.path.join(bin_folder, value)
        self.output.info('Creating %s environment variable: %s' % (name, path))
        return path

    @property
    def toolchainabi(self):
        if self.options.board == 'pico':
            return "arm-pico-eabi"
        elif self.options.board == 'pico2':
            return "arm-pico2-eabi"
        else:
            return ""

    def package_info(self):

        toolchain = os.path.join(self.package_folder, 'x-tools', self.toolchainabi)

        if self.options.board == 'pico':
            cmake_toolchain = os.path.join(toolchain, 'arm-pico-eabi.toolchain.cmake')
        elif self.options.board == 'pico2':
            cmake_toolchain = os.path.join(toolchain, 'arm-pico2-eabi.toolchain.cmake')

        self.output.info('Injecting cmaketoolchain:user_toolchain: %s' % cmake_toolchain)
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", cmake_toolchain)

        self.buildenv_info.define("PICO_SDK_PATH", os.path.join(self.package_folder, "pico-sdk-%s" % self.version))

        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ['bin']
        self.cpp_info.builddirs = ['lib']
