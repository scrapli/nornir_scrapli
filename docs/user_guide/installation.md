# Installation


## Standard Installation

Install the release line that matches your scrapli version:

```
# scrapli v1
pip install "nornir-scrapli>=1,<2"

# scrapli v2
pip install "nornir-scrapli>=2,<3"
```

Without a version constraint, `pip install nornir-scrapli` installs `2026.10.13`, the last calendar-version release,
which receives no further fixes. See [Versioning](versioning.md) for details.


## Installing from a branch

To install the bug fixes for `1.x` from the `main` branch:

```
pip install git+https://github.com/scrapli/nornir_scrapli@main
```

To install the next `1.x` minor release from the `develop-v1` branch:

```
pip install git+https://github.com/scrapli/nornir_scrapli@develop-v1
```

To install the `2.x` line from the `develop` branch:

```
pip install git+https://github.com/scrapli/nornir_scrapli@develop
```


## Installation from Source

To install from source:

```
git clone https://github.com/scrapli/nornir_scrapli
cd nornir_scrapli
pip install .
```


## Supported Platforms

As for platforms to *run* scrapli on -- it has and will be tested on MacOS and Ubuntu regularly and should work on any
 POSIX system. Windows at one point was being tested very minimally via GitHub Actions builds, however this is no
  longer the case as it is just not worth the effort. While scrapli should work on Windows when using the paramiko or
   ssh2-python transport drivers, it is not "officially" supported. It is *strongly* recommended/preferred for folks
    to use WSL/Cygwin instead of Windows.
