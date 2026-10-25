# esphome

ESPHome dashboard + code-server editor for the home-automation microcontrollers,
deployed via Flux (bjw-s app-template) into the `esphome` namespace.

## Setup: one deployment, two containers

The `esphome` deployment runs one pod with **two containers** that share the
network namespace and the `/config` volume:

| Container  | Image                | Purpose |
|------------|----------------------|---------|
| `main`     | esphome dashboard    | Compile + OTA-flash devices; web UI on port 6052, published at `https://esphome.pub.<cluster-domain>/` |
| `editor`   | coder/code-server    | Edit the YAML under `/config` and run `git commit`/`push` for it (port 12321, forward-auth) |

## Persistence

| Mount              | Backend            | Content |
|--------------------|--------------------|---------|
| `/config`          | CephFS PVC         | Git checkout of the device configs (`l17-short-flur-leds.yaml`, `devices/`, `locations/`, `settings/`, `secrets.yaml`, ...) |
| `/config/.esphome` | local xfs disk     | esp-idf build artifacts (CephFS is too slow for builds) |
| `/cache`           | PVC                | platformio/espidf download cache |

## Git in the editor (commit/push)

The `git-ssh-keys` secret (sops-encrypted in `apps/cluster-common`, reflected
into this namespace) carries the keys mounted into the `editor` container:

- `/root/.ssh/id_rsa` — deploy key for `git@github.com:angelnu/esphome.git`
  (tmpfs, read-only).
- `/root/.ssh/known_hosts` — pinned host keys (github.com + the private git
  server). Mounted since 2026-10-25: before, the known_hosts was an ephemeral
  file in the container root and was wiped on every pod restart, so the first
  `git push` after each restart failed with "Please make sure you have the
  correct access rights".

## Workflow

1. **Edit**: code-server (`editor` container) or the dashboard UI.
2. **Compile + OTA-flash**: from the dashboard (`main` container; needs a route
   to the device LAN — it runs on a node with LAN access).
3. **Commit/push**: in the `editor` container — the working tree IS `/config`.
