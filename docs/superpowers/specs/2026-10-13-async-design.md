# Mode-bound Scrapli connections

## Approved behavior

Use one plugin class and connection name for synchronous and asyncio execution:
`ScrapliCore` / `scrapli` and `ScrapliConfig` / `scrapli_cfg`. Register these names
once in Nornir's capability registry. Each instance reports both capabilities,
chooses its driver on open, and lets Nornir record the opening mode.
Opposite-mode acquisition and synchronous cleanup of an asyncio-bound connection
raise Nornir's named mismatch error. Async cleanup dispatches to the matching close
method and retains a failed async close for retry. Synchronous host close follows
Nornir's existing behavior of removing the cache and binding before calling the plugin.
No transparent thread or event-loop bridge is used for device operations.

Add explicit native coroutine tasks in `nornir_scrapli.async_tasks` for the eight
CLI tasks and six Scrapli-Cfg tasks. Preserve arguments, result objects, failure
handling, changed flags, dry-run behavior, and synchronous task imports. NETCONF
remains a separate follow-on. Configuration wrappers reuse the CLI transport;
they do not own or close it, and copy inventory extras before overriding options.

## Implementation decisions

- Target Nornir commit `01bac1d326092489d688a72cd9d19569c6e1688a` from
  `dga/feat-async-spplb`; pin the runtime dependency while upstream support is unreleased.
- Released Nornir 3.6.0 lacks discovery of the new registry despite sharing the
  branch's version number. A version floor alone cannot select the required APIs.
- Default async CLI opening to `asyncssh`, exposed through an optional `asyncio` extra.
- Keep the raw Scrapli driver type so Scrapli-Cfg's exact-type factory continues
  to work. Nornir PR #1111 owns execution-mode binding, cache-hit validation, named
  mismatch errors, and mixed-mode cleanup. Do not duplicate those features in the
  plugin; use the public Host getters and `connection_mode` query.
- Use public host APIs for configuration-wrapper registration, including explicit
  extras carrying the existing CLI driver. No private Nornir cache access.
- Publish connections only on successful open; reclaim partial async opens on
  failure/cancellation. Failed async closes retain transport state for retry.
  Nornir's async cleanup selects `close` for sync-bound connections and `aclose`
  for asyncio-bound connections, retaining failed async cache entries for retry.

## Verification

Exercise real Nornir host caching and runner dispatch, guardrails in both
directions, configuration-wrapper ownership, cancelled/failed opens, close retry,
dry-run and result parity. Run the existing unit suite, real SSH functional tests,
lint, strict typing, documentation build, and distribution build.
