# NETCONF in scrapli v2

NETCONF is part of [scrapli](https://carlmontanari.github.io/scrapli/), using its native
`Netconf` class. nornir_scrapli keeps the `scrapli_netconf` connection name and exposes
18 one-shot tasks. The separate scrapli_netconf package belongs to the v1 ecosystem.

See [Available Tasks](../user_guide/available_tasks.md) and
[Migrating to v2](../user_guide/migrating_to_v2.md) for enum arguments and direct
connection access to subscriptions/notifications.
