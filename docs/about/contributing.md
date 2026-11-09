Contributing
============

Thanks for thinking about contributing! Contributions are not expected, but are quite welcome.

Contributions of all kinds are welcomed -- typos, doc updates, adding examples, bug fixes, and feature adds.


Some notes on contributing:

- Please open a GitHub discussion topic for any potential feature adds/changes to discuss them prior to opening a PR,
  this way everyone has a chance to chime in and make sure we're all on the same page!
- Please open an issue to discuss any bugs/bug fixes prior to opening a PR.
- Once we all have discussed any adds/changes, pull requests are very much welcome and appreciated!
  - All PRs should pass tests/CI linting -- checkout the Makefile for some shortcuts for linting and testing.
  - Please include tests! Even simple/basic tests are better than nothing -- it helps make sure changes in the future
   don't break functionality or make things act in unexpected ways!

## Choosing a target branch

- Bug fixes for `1.x` (scrapli v1): open the pull request against `main`.
- Other changes for the next `1.x` minor release: open the pull request against `develop-v1`.
- Changes for `2.x` (scrapli v2): open the pull request against `develop`.

See the [versioning docs](https://scrapli.github.io/nornir_scrapli/user_guide/versioning) for how releases are made
from these branches.
