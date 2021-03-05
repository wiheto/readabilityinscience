#!/usr/bin/env python
from distutils.core import setup
import setuptools
import os
from setuptools import setup

def read_requirements():
    """parses requirements from requirements.txt"""
    reqs_path = os.path.join(".", "requirements.txt")
    install_reqs = parse_requirements(reqs_path, session=PipSession())
    reqs = [str(ir.req) for ir in install_reqs]
    return reqs


setup(
    name="readability",
    version="1.0",
    description="heavily applied language analysis, tightly coupled with the goal of analysing scientific discourse",
    author="various",
    packages=setuptools.find_packages(),
)
