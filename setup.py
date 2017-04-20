"""A collection of utility methods used by CCBB at UCSD

This project aggregates a collection of python-language utility methods
developed to support the work of the Center for Computational Biology
and Bioinformatics at the University of California at San Diego.
"""

# Much of the content of this file is copied from the
# setup.py of the (open-source) PyPA sample project at
# https://github.com/pypa/sampleproject/blob/master/setup.py

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ccbb_pyutils',

    # Versions should comply with PEP440.
    version='0.3.0',

    description='A collection of utility methods used by CCBB at UCSD',
    long_description=long_description,

    # The project's main homepage.
    url="https://github.com/ucsd-ccbb/ccbb-ucsd-pyutils",

    # Author details
    author='The Center for Computational Biology and Bioinformatics',
    author_email='abirmingham@ucsd.edu',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language:: Python:: 3:: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='development',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed.
    install_requires=['matplotlib','nbformat', 'nbparameterise', 'pandas'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    }
)
