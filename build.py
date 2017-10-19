import platform
from conan.packager import ConanMultiPackager
import os
import cpuid
import copy


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

            opt1 = copy.deepcopy(options)
            opt2 = copy.deepcopy(options)
            opt3 = copy.deepcopy(options)
            opt4 = copy.deepcopy(options)

            opt1["mpir:microarchitecture"] = "x86_64"
            opt2["mpir:microarchitecture"] = ''.join(cpuid.cpu_microarchitecture())
            opt3["mpir:microarchitecture"] = "haswell"
            opt4["mpir:microarchitecture"] = "skylake"

            filtered_builds.append([settings, opt1, env_vars, build_requires])
            filtered_builds.append([settings, opt2, env_vars, build_requires])
            filtered_builds.append([settings, opt3, env_vars, build_requires])
            filtered_builds.append([settings, opt4, env_vars, build_requires])
                
            # filtered_builds.append([settings, options, env_vars, build_requires])
    builder.builds = filtered_builds

    builder.run()
