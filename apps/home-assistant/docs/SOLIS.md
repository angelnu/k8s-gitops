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

1. **Correction (2026-10-11): register 33073 is NOT mislabelled — it is A Phase Voltage**
   (~232 V grid-tied, ~0-1.5 V islanded). The 2026-10-10 session confused it with the
   grid current, which is the separate A Phase Current register
   (`sensor.solis_s6_eh1p_a_phase_current`): 0.5-0.8 A per inverter at standby,
   ~1-1.4 A for both combined — mostly reactive (see [Incident 2026-10-11](#incident-2026-10-11-morning-1-a-draw-with-batteries-at-51)).
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
8. **One string per inverter (2026-10-11)**: each inverter has a single connected string;
   the complementary input reads residual voltage (47-70 V) with 0 A — that is MPPT
   noise, NOT a disconnected/broken string. Do not chase it as an incident (checked
   2026-10-11 afternoon against a suspected primary shadow: the daily aggregate ratios
   were consistent, 1.85 today vs 1.83 yesterday; the primary's midday plateau is
   zero-export curtailment + the secondary taking over in the afternoon, both days).
   The producing string appears on the registers the integration labels `pv_*_2`
   (~114-122 V x 13-14 A) — register string numbering does not match the physical
   connector labels (user's physical input is PV1).

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

## Incident 2026-10-11 morning: "1 A draw with batteries at 51%"

Report: ~1 A of grid consumption with batteries at 51%; the user opened the
differential (11:46 CEST) until the batteries were somewhat charged. Diagnosis from
the recorder data — **nothing was broken**, two separate phenomena were conflated:

1. **The ~1 A reading is reactive standby/magnetising current of both inverters, not
   consumption.** Each inverter's own `a_phase_current` register read 0.5-0.8 A all
   night (Tuya meter `energy_meter_pueblo_phase_a_current`: 0.82-1.07 A every hour,
   at any SOC 52-64%). The active component was only 12-15 W (consumo counter
   +0.01 kWh per ~45 min) — the export calibration fix was holding. It vanishes in
   island mode. For real consumption read `contador_red_electrica_pueblo_potencia`
   (kW) or the consumo counter; the phase-A current sensor is RMS and includes
   reactive current.
2. **The real grid import happened in bursts when SOC reached the ToU cut-off (50%)
   at 10:24.** With the all-day (00:00-23:59) ToU charge slot armed and SOC at the
   cut-off, the inverter inhibits battery discharge (holds the battery at the cut-off)
   and morning house load spikes (1.2-2.4 kW at 10:15-10:45 and 11:10-11:34) fell
   back to the grid: bursts up to 3.1 kW (≈ 14 A), ~0.8 kWh total. Same "load falls
   back to grid" behaviour as finding 4. At 51% the battery was still load-following
   (SOC fell 51→50 with grid at the floor); discharge stopped exactly at 50%, then
   SOC oscillated 50↔51% from 10:24 to 11:35 (PV pushing it just above the cut-off).

Timeline: differential opened 11:46 (island: grid 0 A/0 W, PV 727-1390 W charging the
battery +681 W, house on the backup port 0.7-0.9 A), re-closed 12:15 with SOC 53% and
PV 897 W. If left open with weak PV the battery drains to `off_grid_overdischarge_soc`
(30%) and the house goes dark — re-close physically before evening (finding 6).

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
- For real grid consumption use the Tuya potencia (kW) / consumo (kWh) sensors; the
  phase-A current sensor includes reactive standby current (~1 A for both inverters).
- `battery_power` sensors are unreliable at night (read +265/+450 W "charging" while
  SOC fell 1%/h) — same signed/unsigned bug family as finding 7. Diagnose from SOC
  trend + Tuya meters + PV instead.

## Pending

- [ ] Confirm the <50% grid-charge path still triggers with export calibration = 0
      (next time SOC drops below 50% — expect ~0.95 kW on the Tuya meter).
- [ ] Optionally align the secondary's ToU slot 1 end time (00:00 vs primary 23:59).
