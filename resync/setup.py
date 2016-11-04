#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='resync',
    version='1.0.1',
    packages=['.'],
    install_requires=[
        "requests",
        "python-dateutil>=1.5"
    ],
    url='https://github.com/EHRI/resync/tree/ehribranch',
    license='Apache License 2.0',
    author='Simeon Warner',
    author_email='simeon.warner@cornell.edu',
    description='ResourceSync library and client'
)

