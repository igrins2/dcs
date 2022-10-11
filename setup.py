# -*- coding: utf-8 -*-
'''
Created on April 22 2022

@author: hilee
'''


from setuptools import setup, find_packages


setup(
    name='IGRINS2',
    version='1.0.0',
    author='hilee',
    author_email='hyeinlee@kasi.re.kr',
    description='IGRINS2 Detector Control Software',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
	    "dcs = DCS.DC_cli:CliCommand"
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

