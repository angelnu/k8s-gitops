# Longhorn filesystem

Used to keep local PVCs that do not need to survive the whole cluster going down. These are primarly database nodes and ephemeral volumes.

## Allow node drain

1. Go the cluster settings within the longhorn UI at https://longhorn-ui-longhorn-system.apps.prod.angelnu.com/#/setting
2. Set Node Drain Policy to `allow-if-replica-is-stopped`

NOTE: this should now be set automatically