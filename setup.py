# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

long_description = open('README.rst').read()

setup(
    name='pycomfoconnect',
    version='0.5.1',
    license='MIT',
    url='https://github.com/michaelarnauts/comfoconnect',
    author='Michaël Arnauts',
    author_email='michael.arnauts@gmail.com',
    description='Python interface for the Zehnder ComfoConnect LAN C bridge.',
    long_description=long_description,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=list(val.strip() for val in open('requirements.txt')),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ]
)
