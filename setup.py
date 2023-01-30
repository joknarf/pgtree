#!/usr/bin/env python
"""Install pgtree package"""
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pgtree",
    author="joknarf",
    author_email="joknarf@gmail.com",
    description="Unix process tree search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joknarf/pgtree",
    packages=["pgtree"],
    scripts=["pgtree/pgtree"],
    use_incremental=True,
    setup_requires=['incremental'],
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: Utilities",
    ],
    keywords="shell pstree pgrep process tree",
    license="MIT",
)
