#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.md'),
          encoding='utf-8') as readme_file:
    long_description = readme_file.read()

version = sys.version_info[:2]
if version < (3, 8):
    print('thefuck requires Python version 3.8 or later' +
          ' ({}.{} detected).'.format(*version))
    sys.exit(-1)

VERSION = '3.32.1'

install_requires = ['psutil', 'colorama', 'decorator', 'pyte']
entry_points = {'console_scripts': [
              'thefuck = thefuck.entrypoints.main:main',
              'fuck = thefuck.entrypoints.not_configured:main']}

setup(name='thefuck',
      version=VERSION,
      description="Magnificent app which corrects your previous console command",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Vladimir Iakovlev',
      author_email='nvbn.rm@gmail.com',
      url='https://github.com/baozongwi/thefuck',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples',
                                      'tests', 'tests.*', 'release']),
      include_package_data=True,
      zip_safe=False,
      python_requires='>=3.8',
      install_requires=install_requires,
      entry_points=entry_points)
