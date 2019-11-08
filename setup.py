#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import easymongo

setup(
    name='easymongo',
    version=easymongo.__version__,
    description='Work easier with MongoDB in Python',
    url='https://github.com/catenae/easymongo',
    author='Rodrigo Martínez Castaño',
    author_email='rodrigo@martinez.gal',
    license='GNU General Public License v3 (GPLv3)',
    packages=['easymongo'],
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[''])  # Dependencies
