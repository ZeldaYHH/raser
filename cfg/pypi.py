# -*- encoding: utf-8 -*-
'''
Description:  PyPI     
@created   : 2021/09/08 09:33:59
'''

#test
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="raser",
    version="4.0.1.post2",
    author="Xin Shi",
    author_email="Xin.Shi@outlook.com",
    description="RAdiation SEmiconductoR Detector Simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://raser.team",
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
    ]
	)
