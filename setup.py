#!/usr/bin/env python3
from setuptools import setup
from os import path

# Get Description from readme
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='detcord',
      version='0.1.2',
      description='Redteam Deployment',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/micahjmartin/detcord',
      author='Micah Martin',
      author_email='micahjmartin@outlook.com',
      license='Apache 2.0',
      packages=['detcord'],
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Security',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
      ],
      keywords='deployment redteam security',
      install_requires=[
          'paramiko'
      ],
      scripts=["bin/detonate"],
      project_urls={
          'Bug Reports': 'https://github.com/micahjmartin/detcord/issues',
          'Source': 'https://github.com/micahjmartin/detcord/',
      },
      zip_safe=False)
