#!/usr/bin/env python
"""nornir_scrapli - scrapli nornir plugin"""
import setuptools

__author__ = "Carl Montanari"
__version__ = "2021.01.29"

with open("README.md", "r") as f:
    README = f.read()

with open("requirements.txt", "r") as f:
    INSTALL_REQUIRES = f.read().splitlines()

EXTRAS_REQUIRE = {
    "genie": [],
}

for extra in EXTRAS_REQUIRE:
    with open(f"requirements-{extra}.txt", "r") as f:
        EXTRAS_REQUIRE[extra] = f.read().splitlines()

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
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
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
