#!/usr/bin/env python
"""nornir_scrapli - scrapli nornir plugin"""
import setuptools

from nornir_scrapli import __version__

__author__ = "Carl Montanari"

with open("README.md", "r") as f:
    README = f.read()

setuptools.setup(
    name="nornir_scrapli",
    version=__version__,
    author=__author__,
    author_email="carl.r.montanari@gmail.com",
    description="scrapli Nornir plugin",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/carlmontanari/nornir_scrapli",
    packages=setuptools.find_packages(),
    install_requires=["scrapli>=2020.06.06", "nornir>=3.0.0a0"],
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
    entry_points="""
    [nornir.plugins.connections]
    scrapli=nornir_scrapli.connection:Scrapli
    """,
)
