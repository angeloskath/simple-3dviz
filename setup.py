#!/usr/bin/env python

"""Setup simple-3dviz"""

from itertools import dropwhile
import os
from os import path
from setuptools import find_packages, setup


def collect_docstring(lines):
    """Return document docstring if it exists"""
    lines = dropwhile(lambda x: not x.startswith('"""'), lines)
    doc = ""
    for line in lines:
        doc += line
        if doc.endswith('"""\n'):
            break

    return doc[3:-4].replace("\r", "").replace("\n", " ")


def collect_metadata():
    meta = {}
    with open(path.join("simple_3dviz", "__init__.py")) as f:
        lines = iter(f)
        meta["description"] = collect_docstring(lines)
        for line in lines:
            if line.startswith("__"):
                key, value = map(lambda x: x.strip(), line.split("="))
                meta[key[2:-2]] = value[1:-1]

    return meta


def get_extensions():
    return []


def get_install_requirements():
    return [
        "moderngl",
        "numpy",
        "pyrr",
        "plyfile",
        "Pillow"
    ]


def setup_package():
    with open("README.md") as f:
        long_description = f.read()
    meta = collect_metadata()
    setup(
        name="simple-3dviz",
        version=meta["version"],
        description=meta["description"],
        long_description=long_description,
        long_description_content_type="text/markdown",
        maintainer=meta["maintainer"],
        maintainer_email=meta["email"],
        url=meta["url"],
        keywords=meta["keywords"],
        license=meta["license"],
        classifiers=[
            "Intended Audience :: Science/Research",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Topic :: Scientific/Engineering",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
        ],
        packages=find_packages(exclude=["docs", "tests", "scripts"]),
        install_requires=get_install_requirements(),
        ext_modules=get_extensions(),
        entry_points={
            "gui_scripts": [
                "mesh_viewer = simple_3dviz.scripts.mesh_viewer:main",
                "func_viewer = simple_3dviz.scripts.func_viewer:main"
            ]
        }
    )


if __name__ == "__main__":
    setup_package()
