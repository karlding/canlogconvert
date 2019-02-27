#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages


def find_version():
    return "0.1.0"


setup(
    name="canlogconvert",
    version=find_version(),
    description="",
    long_description=open("README.md", "r").read(),
    author="Karl Ding",
    author_email="",
    license="MIT",
    classifiers=[],
    keywords=["can"],
    url="https://github.com/karlding/canlogconvert",
    packages=find_packages(exclude=["tests"]),
    install_requires=["pyparsing>=2.3.1"],
    test_suite="tests",
    entry_points={"console_scripts": ["canlogconvert=canlogconvert.__init__:_main"]},
)
