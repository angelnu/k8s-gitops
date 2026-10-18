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
- [x] **homematic → homematic(IP) Local** (`homematicip_local`, HACS) — DONE
  2026-10-18: entities migrated to the new integration and all references
  migrated with them — dashboard (clima/windows macros, floorplan boiler
  switch icons and weather badges), clima package template sensors, `boiler.py`
  (valve discovery on `climate.<room>_valve_*` + readings from the
  `sensor.*_valve_opening` sensors — these are disabled-by-default by the
  integration and had to be enabled in the entity registry), `boiler.yaml`
  (`boilerControl` on the `homematicip_local` PCBS switch channels), kitchen
  extractor switch (`switch.kitchen_kitchenextractor`), covers (incl. the
  outdoor weather sensor temperature), watering apps, google assistant, and the
  AppDaemon button apps (`buttons_light`, `buttons_cover`,
  `buttons_homematic_music`, `buttons_homematic_climate`) now
  listening on the new `event.*` entities instead of `homematic.keypress`.
  The legacy pyhomematic integration is disabled (commented out in
  `packages/homematic.yaml`, kept for re-enable). Remaining: physical
  button-press field test (e.g. kitchen mute); optional cleanup of the ~260
  orphaned legacy entities still in the entity registry (they currently cause
  "Referenced entities ... missing" warning noise from setTemperature).

## Notes

- The LDAP outpost is still used by other apps (maddy, tt-rss) — do not remove.
- Full migration runbook: `infrastructure/docs/plans/ha-oidc-migration.md`.
