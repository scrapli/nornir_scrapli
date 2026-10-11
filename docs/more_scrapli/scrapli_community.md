# Custom platforms

scrapli v2 deprecates the separate scrapli_community package. Device behavior is
defined in YAML, including modes, prompts, failure indicators and on-open instructions.

Use `extras.definition: ./my_platform.yaml` to select a custom definition. See the
[scrapli documentation](https://carlmontanari.github.io/scrapli/) and
[Migrating to v2](../user_guide/migrating_to_v2.md).
