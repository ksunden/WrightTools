#! /usr/bin/env python3

from setuptools import setup, find_packages

version = "0.0.0"

setup(
    name="WrightTools",
    packages=find_packages(),
    python_requires=">=3.5",
    version=version,
    tests_require=["pytest"],
    author="Kyle Sunden",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
