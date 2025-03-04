# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='pylkmotor',
    version='1.0.2',
    author='Xudong Han',
    description='Python library for controlling LK motors',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/han-xudong/pyLKMotor',
    packages=find_packages(),
    install_requires=['python-can>=4.5.0'],
    python_requires='>=3.10',
    keywords=['LK motor', 'robotics'],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)