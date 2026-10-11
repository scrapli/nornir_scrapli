# Installation

## Standard installation

```shell
pip install nornir-scrapli
```

The v2 line requires Python 3.10 or newer and `scrapli>=2026.10.8`. Python 3.10–3.14
is tested. Install optional Genie parsing support with `pip install 'nornir-scrapli[genie]'`.
TextFSM and ntc-templates are installed by default.

## Installation from source

```shell
pip install git+https://github.com/scrapli/nornir_scrapli.git@main
```

For a local checkout use `pip install -e .`, or use the repository's uv/nox workflow
described in the contributing guide.

## Supported platforms

scrapli v2 uses libscrapli native wheels for Linux x86_64/aarch64 (glibc and musl) and
macOS Apple silicon. Windows and Intel macOS are unsupported. Choose a supported
Linux environment when running automation from an unsupported desktop platform.

Upgrading from v1 requires changes to inventory extras and task arguments. Follow
[Migrating to v2](migrating_to_v2.md). Users needing the removed `cfg_*` tasks stay on
`nornir-scrapli==2026.10.10`.
