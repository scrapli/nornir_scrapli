# Installation


## Standard Installation

Install the release line that matches your scrapli version:

```
# scrapli v1
pip install "nornir-scrapli>=1,<2"

# scrapli v2
pip install "nornir-scrapli>=2,<3"
```

Each `1.x` release is also published with a calendar version, such as `2026.10.30`. Without a version constraint,
`pip install nornir-scrapli` installs the latest calendar version, which uses scrapli v1. Calendar versions will later
follow `2.x` instead. See [Versioning](versioning.md) for details.

The `2.x` line requires Python 3.10 or newer and `scrapli>=2026.10.8`. Python 3.10–3.14
is tested. Install optional Genie parsing support with `pip install 'nornir-scrapli[genie]'`.
TextFSM and ntc-templates are installed by default.


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

For development, use the repository's uv/nox workflow described in the contributing guide.


## Supported Platforms

scrapli v2 uses libscrapli native wheels for Linux x86_64/aarch64 (glibc and musl) and
macOS Apple silicon. Windows and Intel macOS are unsupported. Choose a supported
Linux environment when running automation from an unsupported desktop platform.

Upgrading from `1.x` requires changes to inventory extras and task arguments. Follow
[Migrating to v2](migrating_to_v2.md). Users needing the removed `cfg_*` tasks stay on
`nornir-scrapli>=1,<2`.
