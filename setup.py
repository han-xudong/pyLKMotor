# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='pylkmotor',
    version='1.0.0',
    description='Python library for controlling LK motors',
    author='Xudong Han',
    url='https://github.com/han-xudong/pyLKMotor',
    packages=find_packages(),
    install_requires=['python-can>=4.5.0'],
    python_requires='>=3.6',
    keywords=['LK motor', 'robotics'],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)