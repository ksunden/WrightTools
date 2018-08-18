#! /usr/bin/env python3

from setuptools import setup, find_packages

version = "0.0.0"

setup(
    name="WrightTools",
    packages=find_packages(exclude=("tests", "tests.*")),
    python_requires=">=3.5",
    setup_requires=["pytest-runner"],
    tests_require=[
        "pytest",
    ],
    version=version,
    author="WrightTools Developers",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
    ],
)
