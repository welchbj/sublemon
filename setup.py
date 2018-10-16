"""Setup configuration for the `sublemon` library."""

import codecs
import os

from setuptools import (
    find_packages,
    setup)

HERE = os.path.abspath(os.path.dirname(__file__))
SUBLEMON_DIR = os.path.join(HERE, 'sublemon')
VERSION_FILE = os.path.join(SUBLEMON_DIR, 'version.py')

with codecs.open(VERSION_FILE, encoding='utf-8') as f:
    exec(f.read())
    version = __version__  # noqa

setup(
    name='sublemon',
    version=version,
    description='Local asynchronous subprocess generation as a Python library',
    long_description='Visit the project\'s home page for more information',
    author='Brian Welch',
    author_email='welch18@vt.edu',
    url='https://github.com/welchbj/sublemon',
    license='MIT',
    install_requires=['aiostream'],
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    include_package_data=True,
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ]
)
