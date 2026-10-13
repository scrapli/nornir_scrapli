# Mode-bound Scrapli connections

## Approved behavior

Use one plugin class and connection name for synchronous and asyncio execution:
`ScrapliCore` / `scrapli` and `ScrapliConfig` / `scrapli_cfg`. Register these names
once in Nornir's capability registry. Each instance reports both capabilities,
chooses its driver on open, and retains that mode until successful close.
Wrong-mode task acquisition and lifecycle operations raise a named error with
instructions to close and reopen. No transparent thread or event-loop bridge is used.

Add explicit native coroutine tasks in `nornir_scrapli.async_tasks` for the eight
CLI tasks and six Scrapli-Cfg tasks. Preserve arguments, result objects, failure
handling, changed flags, dry-run behavior, and synchronous task imports. NETCONF
remains a separate follow-on. Configuration wrappers reuse the CLI transport;
they do not own or close it, and copy inventory extras before overriding options.

## Implementation decisions

- Target Nornir commit `f62f07aab4a1285c4c1e918151c3476472b15a84` from
  `dga/feat-async-spplb`; pin the runtime dependency while upstream support is unreleased.
- Released Nornir 3.6.0 lacks discovery of the new registry despite sharing the
  branch's version number. A version floor alone cannot select the required APIs.
- Default async CLI opening to `asyncssh`, exposed through an optional `asyncio` extra.
- Keep the raw Scrapli driver type so Scrapli-Cfg's exact-type factory continues
  to work. Guards cover this package's tasks and plugin lifecycle. Raw-driver
  access is not intercepted; Nornir itself currently returns opposite-mode cache hits.
- Nornir's documented dual-capability contract assumes cross-mode transport reuse.
  This package instead implements the explicitly approved mode-bound policy;
  documentation must explain that distinction and the upstream integration limit.
- Use public host APIs for configuration-wrapper registration, including explicit
  extras carrying the existing CLI driver. No private Nornir cache access.
- Publish connections only on successful open; reclaim partial async opens on
  failure/cancellation. Failed closes retain state for retry. Wrong-mode closing
  raises too; mixed-mode inventories require explicit cleanup through the matching
  host/plugin lifecycle operations.

## Verification

Exercise real Nornir host caching and runner dispatch, guardrails in both
directions, configuration-wrapper ownership, cancelled/failed opens, close retry,
dry-run and result parity. Run the existing unit suite, real SSH functional tests,
lint, strict typing, documentation build, and distribution build.
