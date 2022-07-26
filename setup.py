#!/usr/bin/env python
"""nornir_scrapli"""
from copy import copy

import setuptools

__version__ = "2022.07.30"
__author__ = "Carl Montanari"

with open("README.md", "r", encoding="utf-8") as f:
    README = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    INSTALL_REQUIRES = f.read().splitlines()

EXTRAS_REQUIRE = {
    "genie": [],
}

for extra in copy(EXTRAS_REQUIRE):
    with open(f"requirements-{extra}.txt", "r", encoding="utf-8") as f:
        EXTRAS_REQUIRE[extra] = f.read().splitlines()

full_requirements = [requirement for extra in EXTRAS_REQUIRE.values() for requirement in extra]
EXTRAS_REQUIRE["full"] = full_requirements


setuptools.setup(
    name="nornir_scrapli",
    version=__version__,
    author=__author__,
    author_email="carl.r.montanari@gmail.com",
    description="Scrapli's plugin for Nornir",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="ssh telnet netconf automation network cisco iosxr iosxe nxos arista eos juniper "
    "junos",
    url="https://github.com/scrapli/nornir_scrapli",
    project_urls={
        "Docs": "https://scrapli.github.io/nornir_scrapli/",
    },
    license="MIT",
    package_data={"nornir_scrapli": ["py.typed"]},
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    dependency_links=[],
    extras_require=EXTRAS_REQUIRE,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    entry_points="""
    [nornir.plugins.connections]
    scrapli=nornir_scrapli.connection:ScrapliCore
    scrapli_cfg=nornir_scrapli.connection:ScrapliConfig
    scrapli_netconf=nornir_scrapli.connection:ScrapliNetconf
    """,
)
