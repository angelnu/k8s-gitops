# home-assistant

Home automation (Home Assistant) + appdaemon on OKD, deployed via Flux (bjw-s app-template).

## Authentication (OIDC via authentik)

Login is **SSO-only** through authentik (`christiaangoossens/hass-oidc-auth`, HACS) —
there is **no local login**. Full details (groups and access, member management,
recovery runbook without authentik, upstream status):
[`docs/auth-oidc.md`](docs/auth-oidc.md).

Other docs:

- [`docs/SOLIS.md`](docs/SOLIS.md) — Solis solar setup (2x S6-EH1P): findings, final
  configuration and evidence from the 2026-10-10/11 tuning session.

## ToDo

- [ ] **ef_ble (EcoFlow EF-P31574)**: entry disabled (2026-10-04, `disabled_by: user`)
  because setup fails with "Stored configuration is missing the device user ID".
  Pending: check if the device user ID can be recovered/extracted — if not,
  remove the device and pair it again to repair the config entry.
- [ ] **homematic → homematic(IP) Local** (`homematicip_local`, HACS): replace the
  deprecated pyhomematic-based `homematic` integration (unmaintained library,
  blocking RPC calls stall the event loop). Supports OpenCCU/CCU3/RaspberryMatic
  over XML-RPC and multiple CCUs (covers `rf` + `rf_pueblo`). Creates NEW
  entities — migrate references progressively (automations, lovelace, AppDaemon
  apps: `dimmer_*`, `buttons_*`, `boiler` reading `climate.valve_*`), then
  disable the legacy integration.

## Notes

- The LDAP outpost is still used by other apps (maddy, tt-rss) — do not remove.
- Full migration runbook: `infrastructure/docs/plans/ha-oidc-migration.md`.
