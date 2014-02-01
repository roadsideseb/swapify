#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='swapify',
    version="0.1.1",
    url='https://github.com/elbaschid/swapify',
    author="Sebastian Vetter",
    author_email="sebastian@roadside-developer.com",
    description="Make migrations work with swappable models.",
    long_description='\n\n'.join([
        open('README.rst').read(),
        open('CHANGELOG.rst').read(),
    ]),
    license='MIT',
    platforms=['linux'],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=[
        'docopt',
    ],
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': ['swapify = swapify.cli:main']
    },
)
