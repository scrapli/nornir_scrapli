#!/usr/bin/env python
"""nornir_scrapli - scrapli nornir plugin"""
import setuptools

__author__ = "Carl Montanari"

with open("README.md", "r") as f:
    README = f.read()

setuptools.setup(
    name="nornir_scrapli",
    version="2020.04.05",
    author=__author__,
    author_email="carl.r.montanari@gmail.com",
    description="scrapli Nornir plugin",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/carlmontanari/nornir_scrapli",
    packages=setuptools.find_packages(),
    # install_requires=["scrapli>=2020.03.21", "nornir>=3.0.0"],
    install_requires=["scrapli>=2020.03.21", "nornir>=2.4.0"],
    extras_require={},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
)
