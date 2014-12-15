import sys

if sys.version < '3.4':
    print('Sorry, this is not a compatible version of Python. Use 3.4 or later.')
    exit(1)

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

with open('README.md') as f:
    description = f.read()

from diana import VERSION

setup(name='libdiana',
      version=VERSION,
      description='Library for talking to Artemis SBS.',
      author='Alistair Lynn',
      author_email='arplynn@gmail.com',
      license="MIT",
      long_description=description,
      url='https://github.com/prophile/libdiana',
      zip_safe=True,
      setup_requires=['nose >=1.0'],
      packages=find_packages())

