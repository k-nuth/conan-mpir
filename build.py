import platform
from conan.packager import ConanMultiPackager
import os
import cpuid
import copy

def handle_microarchs(opt_name, microarchs, filtered_builds, settings, options, env_vars, build_requires):
    print(microarchs)
    microarchs = list(set(microarchs))
    print(microarchs)

    for ma in microarchs:
        opts_copy = copy.deepcopy(options)
        opts_copy[opt_name] = ma
        filtered_builds.append([settings, opts_copy, env_vars, build_requires])

if __name__ == "__main__":
    builder = ConanMultiPackager(username="bitprim", channel="stable",
                                 remotes="https://api.bintray.com/conan/bitprim/bitprim")
    builder.add_common_builds(shared_option_name="mpir:shared", pure_c=True)
    builder.password = os.getenv("CONAN_PASSWORD")

    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if settings["build_type"] == "Release" \
                and settings["arch"] == "x86_64" \
                and not ("mpir:shared" in options and options["mpir:shared"]):

            marchs = ["x86_64", ''.join(cpuid.cpu_microarchitecture()), "haswell", "skylake"]
            handle_microarchs("mpir:microarchitecture", marchs, filtered_builds, settings, options, env_vars, build_requires)
                
    builder.builds = filtered_builds

    builder.run()
