# Scrapli Replay

This page describes the v1 ecosystem. scrapli v2 has native recording/test transport
options; nornir_scrapli's unit tests patch native methods. Recorded-session/device
testing is tracked separately in [issue #172](https://github.com/scrapli/nornir_scrapli/issues/172).


[scrapli_replay](https://github.com/scrapli/scrapli_replay) ([docs](https://scrapli.github.io/scrapli_replay/)) 
is a set of tools used to help test scrapli programs. scrapli_replay includes a utility to capture command 
input/output from real life servers and replay them in a semi-interactive fashion, as well as a pytest plugin that 
patches and records and replays session data (like [vcr.py](https://github.com/kevin1024/vcrpy)) for scrapli connections. 
