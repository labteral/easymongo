#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from pathlib import Path
import re

ROOT = Path(__file__).parent
VERSION = re.search(r'''^__version__ = ['"]([^'"]+)['"]''',
                    (ROOT / 'easymongo/__init__.py').read_text(), re.M)[1]

setup(
    name='easymongo',
    version=VERSION,
    long_description='MongoDB helpers for connections, queries and bounded health checks.',
    long_description_content_type='text/plain',
    python_requires='>=3.10,<4',
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
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=['pymongo>=4.2.0,<5.0.0', 'dnspython>=2.1.0,<3.0.0'])
