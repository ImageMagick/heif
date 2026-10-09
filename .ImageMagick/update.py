#!/usr/bin/env python3
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Tools"))

from dependency_updater import Step, UpdateError, Updater

URL = "https://github.com/strukturag/libheif/archive/refs/tags/v{version}.tar.gz"


def update_source(updater):
    updater.replace_source()
    updater.remove(".github")
    updater.update_config()


def create_header(updater):
    updater.cmake(
        "-DBUILD_SHARED_LIBS=OFF",
        "-DBUILD_TESTING=OFF",
        "-DWITH_EXAMPLES=OFF",
        "-DENABLE_PLUGIN_LOADING=OFF",
        "-DWITH_JPEG_DECODER=OFF",
        "-DWITH_JPEG_ENCODER=OFF")
    updater.copy_from_build("libheif", ["heif_version.h"], "libheif")
    updater.remove_build()


def nclx_profile_fields(updater):
    text = (updater.dependency_dir / "libheif/nclx.h").read_bytes().decode("utf-8")
    match = re.search(r"^struct nclx_profile\r?\n\{\r?\n(.*?)^\};", text, re.M | re.S)
    if not match:
        raise UpdateError("unable to find struct nclx_profile in libheif/nclx.h")
    fields = re.findall(r"^  [\w:<>]+\s+(m_\w+)\s*(?:=[^;]*)?;", match.group(1), re.M)
    if not fields:
        raise UpdateError("unable to find the fields of struct nclx_profile in libheif/nclx.h")
    print(f"Fields of nclx_profile: {', '.join(fields)}")
    return fields


def fix_cpp20(updater):
    fields = nclx_profile_fields(updater)
    comparison = " &&\n           ".join(f"{field} == b.{field}" for field in fields)
    updater.replace_in_file("libheif/nclx.h",
        "  bool operator==(const nclx_profile& b) const = default;",
        "  bool operator==(const nclx_profile& b) const {\n"
        f"    return {comparison};\n"
        "  }")
    updater.replace_in_file("libheif/nclx.h",
        "  bool operator!=(const nclx_profile& b) const = default;",
        "  bool operator!=(const nclx_profile& b) const { return !(*this == b); }")


updater = Updater(__file__, "libheif", URL)
updater.run([
    Step("Replace the source with the release and update Config.txt", update_source,
        "Updated libheif to {version}"),
    Step("Use cmake to create the header file", create_header,
        "Created header file with cmake."),
    Step("Fix the linux build that doesn't fully support c++20", fix_cpp20,
        "Patch to fix the linux build that doesn't fully support c++20."),
    updater.clone_dependencies_step(),
])
