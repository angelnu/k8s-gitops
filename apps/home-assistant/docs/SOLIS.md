# Solis solar setup (2x S6-EH1P) — findings & configuration

Two Solis S6-EH1P hybrid inverters, monitored/controlled from Home Assistant via the
`solis_modbus` integration (HACS, v4.2.6) over Modbus TCP port 502. This doc records the
tuning session of 2026-10-10/11 and the final configuration.

**Goal**: zero grid draw whenever battery SOC > 50%; charge from grid only when SOC < 50%
(ToU charge slot, 5 A). No peak shaving needed. Never isolate the inverter remotely
(fail-closed risk — see [Differential](#differential)).

## Devices

| Config entry | Host | Slave | Role | Poll profile |
|---|---|---|---|---|
| `Solis: 1031260253071702` | 192.168.105.76 | 1 | Primary | `full` |
| `Solis: 1031260256250133` | 192.168.105.72 | 2 | Secondary | `full` (was `essential`, switched 2026-10-11) |

- Metering ground truth: Tuya devices **"Contador Red Electrica"** (energy meter on the feed
  between utility grid and the Solis grid port; also the differential relay switch) and
  **"Contador Casa Pueblo"** (3-phase breaker metering the house).
- The Solis EPM clamp is on the **grid feed** (time-aligned match with the Tuya meter,
  685 W vs 715 W peak), NOT on the backup output (which carries ~120-760 W).

## Final configuration (both inverters, verified 2026-10-11)

| Parameter | Primary | Secondary |
|---|---|---|
| Storage mode | Self-Use | Self-Use |
| Export calibration (reg 43195) | **0 W** (was -30) | 0 W |
| ToU charge slot 1 | ON 00:00-23:59 · 5 A · cut-off SOC 50% | ON · 50 A · cut-off SOC 50% |
| ToU discharge slots | all OFF | all OFF |
| Peak shaving | OFF | OFF |
| Peak max usable grid power | 15000 W | 15000 W |
| Allow export (self-gen) | OFF | OFF |
| Allow grid to charge battery | ON | ON |
| Tuya differentials | ON | ON |

## Key findings

1. **Register 33073 is mislabelled** "A Phase Voltage" in this firmware — it is actually the
   grid current (0.6-0.8 ≈ 0.7 A standby). Confirmed with an independent clamp meter.
2. **Night standby (~70-100 W) is hardware auxiliary consumption** drawn directly from the
   grid terminals. The firmware ignores all export/zero-export/peak control parameters for
   it. It only disappears in island mode (differential open), where the battery covers ~230 W.
3. **Export calibration (register 43195, S16, range -1000..+1000 W) was the actual fix.**
   The -30 W offset biased the regulation point so ~88 W leaked from the grid all night.
   Setting it to 0 moved the whole night load onto the battery: grid went from ~92 W average
   to ~10-13 W (meter noise floor). Writing +10 made no measurable difference and was
   reverted to 0 (neutral regulation point).
4. **ToU forced discharge does NOT work as a load-following mechanism here**: with a charge
   period enabled (all-day overlap) the discharge switch reverts to OFF after ~60 s (inverter
   validation cycle); with charge disabled the discharge stays ON but *replaces*
   load-following — battery drops to 0 W and backup load falls back to grid (260-307 W).
   Reverted. Do not retry.
5. **No auto "island until SOC low" mode exists** on this hardware (anti-islanding per
   VDE-AR-N 4105; storage-mode options are Self-Use / Feed-in Priority / Off-Grid /
   Peak Shaving only). The <50% grid-charge behaviour comes from the ToU charge slot
   with cut-off SOC.
6. **Differential**: never switch the Tuya differentials off remotely. If HA/remote access is
   down the island would strand the house with no way to re-close them. They are left ON and
   are only operated physically.
7. **Entity bug**: `sensor.solis_s6_eh1p_backup_load_power` shows 65446 W — a signed/unsigned
   bug (S16 0xFFA6 = -90 W read as U16). Known quirk of the integration.

## Evidence (night 2026-10-10 → 11, Tuya "Contador Red Electrica")

Export calibration -30 → 0 written at ~00:32 CEST:

| Hour | Grid avg | Grid max |
|---|---|---|
| 23h (before) | 92 W | 104 W |
| 00h (fix 00:32) | 53 W | 110 W |
| 01h | 13 W | 38 W |
| 02h | 11 W | 29 W |
| 03h | 10 W | 26 W |
| 04h | 9 W | 30 W |
| 05h | 13 W | 35 W |
| 06h | 11 W | 30 W |
| 07h | 12 W | 36 W |
| 08h | 13 W | 40 W |

- Overnight SOC 62% → 52% while batteries covered the ~194 W house load; grid stayed at the
  ~10-13 W measurement floor. Grid import in 24 h: ~0.1 kWh (vs ~2 kWh/day before → ~95%
  reduction, ≈ 9-14 €/month saved).
- Recharge path verified on 10 oct 18:58-19:02: SOC < 50% → grid charge kicked in at
  ~0.95 kW (5 A slot), then grid back to ~1-2 W once repurchased. (With calibration=0 this
  path is still pending one confirmation.)

## Secondary inverter: `essential` → `full` profile (2026-10-11)

The secondary only exposed 141 of 573 entities because its config entry used
`poll_profile: essential` (skips the 43xxx holding groups, so all writable entities —
storage mode, export calibration, ToU slots — are deliberately not created).

Changed via the integration options flow over the HA HTTP API:

```sh
# 1. start the options flow (handler = config entry_id)
POST /api/config/config_entries/options/flow   {"handler": "<entry_id>"}
# 2. submit all fields, only changing poll_profile
POST /api/config/config_entries/options/flow/<flow_id>   {"poll_profile": "full", ...}
# 3. apply
POST /api/services/homeassistant/reload_config_entry   {"entry_id": "<entry_id>"}
# 4. a full restart of HA is needed for every entity to materialise
```

Gotchas:
- Options are stored in `entry.options` and merged over `entry.data` at runtime — after the
  flow, `entry.data.poll_profile` still reads `essential`; that is fine.
- The ws command `config_entries/options/init` does NOT exist (unknown_command) — use the
  HTTP endpoints above. Same for `config_entries/reload`.
- New entities are named from the device name (`pueblo_inversor_solis_secundario_*`) while
  pre-existing ones keep their old ids (`solis_s6_eh1p_*_2`). Mixed naming — dashboards and
  automations need both prefixes.

## Ops notes (HA runs on OKD, namespace `home-assistant`)

- HA data in CloudNativePG cluster `home-assistant-db`; **PRIMARY is `home-assistant-db-3`**
  (db-1/db-2 are replicas — query the primary or you get stale data). `psql -U postgres -d app`.
- States table `last_updated_ts` is epoch double precision: use `to_timestamp(...)`.
- HA API access: exec into `deploy/appdaemon -c main` and curl `http://home-assistant-main:8123`
  with `Authorization: Bearer $TOKEN` (long-lived token from the appdaemon env, no value here).
- Direct Modbus writes: service `solis_write_holding_register` (address, value, host, slave).
- The datalogger can hang/lock the Modbus bus (app cloud theory); reloading both config
  entries via `reload_config_entry` restores polling (`last_modbus_success` goes fresh).
- Register references: 43195 export calibration; 43707 ToU enable bitmask (bit 6 = discharge
  period 1); register definitions in the integration at
  `/config/custom_components/solis_modbus/sensor_data/` inside the HA pod.

## Pending

- [ ] Confirm the <50% grid-charge path still triggers with export calibration = 0
      (next time SOC drops below 50% — expect ~0.95 kW on the Tuya meter).
- [ ] Optionally align the secondary's ToU slot 1 end time (00:00 vs primary 23:59).
