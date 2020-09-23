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
    url="https://github.com/scrapli/nornir_scrapli",
    packages=setuptools.find_packages(),
    install_requires=[
        "scrapli>=2020.06.06",
        "scrapli_community>=2020.08.08",
        "scrapli_netconf>=2020.09.23",
        "nornir>=3.0.0,<4.0.0",
    ],
    extras_require={
        "textfsm": ["textfsm>=1.1.0,<2.0.0", "ntc-templates>=1.1.0,<2.0.0"],
        "genie": ["genie>=20.2", "pyats>=20.2"],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
    entry_points="""
    [nornir.plugins.connections]
    scrapli=nornir_scrapli.connection:ScrapliCore
    scrapli_netconf=nornir_scrapli.connection:ScrapliNetconf
    """,
)
