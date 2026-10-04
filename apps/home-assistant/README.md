# home-assistant

Home automation (Home Assistant) + appdaemon on OKD, deployed via Flux (bjw-s app-template).

## Authentication (OIDC via authentik)

Login is **SSO-only** through authentik (`christiaangoossens/hass-oidc-auth`, HACS).
There is **no local login** — `homeassistant: auth_providers: []` in
`/config/configuration.yaml` (PVC), and local password hashes have been purged.

Access control lives in authentik (managed in the `infrastructure` repo,
`terraform/authentik/` + `settings/authentik.yaml`):

| Group       | Members                          | Access                                   |
|-------------|----------------------------------|------------------------------------------|
| `ha-users`  | all HA users (alicia, angel, angelnb, daniel, eduardo, javier, kiosk, luisa, mireille) | Can log in to Home Assistant (standard user) |
| `ha-admins` | angel, javier, mireille          | Can log in + gets `system-admin` role in HA (`auth_oidc.roles.admin`) |

Access is enforced by policy bindings on the authentik `Home Assistant`
application (`app-homeassistant.tf`). Add/remove members by editing
`settings/authentik.yaml` (`sops`) and running `terraform apply` in the
infrastructure repo.

New users: while `features.automatic_user_linking: true` remains set, a first
SSO login links to the existing HA account with the same username.

## Recovery (no authentik / OIDC broken)

Direct login is intentionally impossible without authentik. Recovery is done
from the cluster itself:

```sh
kubectl -n home-assistant exec -it deploy/home-assistant -c main -- sh
# in /config/configuration.yaml temporarily set:
#   homeassistant:
#     auth_providers:
#       - type: homeassistant
kubectl -n home-assistant rollout restart deployment home-assistant
# create/reset a local admin password if needed:
kubectl -n home-assistant exec -it deploy/home-assistant -c main -- \
  hass --script auth --config /config --username <user> --password <pass>
# log in via the local form, then revert the configuration.yaml change
```

Pre-migration auth backups (old password store, ldap-auth.py, auth_header
component, configuration.yaml.bak-*) were **deleted on 2026-10-04** after all
users completed SSO linking. `automatic_user_linking` is now `false`: new
authentik users (if added to `ha-users`) get a *fresh* HA profile on first
login; re-enable linking temporarily only if you need to bind an existing HA
account.

## ToDo

- [ ] **ef_ble (EcoFlow EF-P31574)**: entry disabled (2026-10-04, `disabled_by: user`)
  because setup fails with "Stored configuration is missing the device user ID".
  Pending: check if the device user ID can be recovered/extracted — if not,
  remove the device and pair it again to repair the config entry.

## Upstream

- Feature request (pairing screen UX on companion apps — "Continue on this
device" in-WebView login): christiaangoossens/hass-oidc-auth **discussion #431**
  (https://github.com/christiaangoossens/hass-oidc-auth/discussions/431)

## Notes

- The LDAP outpost is still used by other apps (maddy, tt-rss) — do not remove.
- Full migration runbook: `infrastructure/docs/plans/ha-oidc-migration.md`.
