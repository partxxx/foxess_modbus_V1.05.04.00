# Testing the EXPERIMENTAL unified Modbus map

FoxESS has published a Modbus definition, **V1.05.04.00 (2025-12-15)**. It describes one register map
across its hybrid families, with per-family limits noted for KH, H1, H1-G2 and the Smart series. This
integration currently uses a separate, partly reverse-engineered map for each family.

This test build adds an **opt-in, read-only** switch that makes the integration read your inverter through
the documented map instead. The goal is to find out, family by family, whether the new map works. Only then
should any change be proposed upstream.

> **Status: experimental.** It has been verified on one inverter only: an H3-5.0-E, Master 2.23, Slave 1.03,
> Manager 1.95. Every other family is untested. That is what we need you for.

- [What the switch does](#what-the-switch-does)
- [Is my inverter included?](#is-my-inverter-included)
- [Safety](#safety)
- [Install the test build](#install-the-test-build)
- [Test procedure](#test-procedure)
- [What to check](#what-to-check)
- [Reporting](#reporting)
- [Going back](#going-back)
- [Known limitations and open questions](#known-limitations-and-open-questions)
- [Technical notes](#technical-notes)

Full entity list with registers and scaling: [unified-map-entities.md](unified-map-entities.md).

---

## What the switch does

**Settings → Devices & services → FoxESS - Modbus → Configure → (your inverter) → Advanced options →
"EXPERIMENTAL: use the unified FoxESS Modbus map (V1.05.04.00)"**

When the switch is **on**:

- All entities come from the documented map: every register read is 36000 or above, outside
  40000–44999. The old per-family registers (31xxx, 32xxx, 41xxx, 44xxx) are not read at all.
- **No write controls.** There are no work mode, charge or discharge current, SoC limit, export limit or
  balance mode controls, no charge periods, and no remote control / force charge / force discharge. The
  charge period services refuse with "Inverter does not support setting charge periods". The generic
  `foxess_modbus.write_registers` service still writes exactly what you call it with, as always.
- The switch **overrides the firmware version setting.** While it is on, the version selector has no effect.
- Single-phase models get the R-phase entities, with keys ending in `_R`. The S- and T-phase entities
  are left out.
- Entities whose registers are known to be missing on your family are not created (see
  [Technical notes](#technical-notes)).

When the switch is **off**, everything is exactly as before. For every model and firmware version, the
normal entity set was checked to be byte-identical to the build without this feature.

The integration reloads when you save the options. Entities of the normal map that don't exist on the
unified map become _unavailable_, and come back when you switch it off again.

## Is my inverter included?

The switch appears only for models whose current firmware is expected to use the new map.

| Map              | Models                                                                                                                                  | Entities                                       |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Unified, 3-phase | H3 (any firmware setting; expected to work from Manager 1.93), AC3, H3-Smart / H3-M, P3-S (P3-x.x-SH), SK-HWR-Smart, Enpal I-X, 1KOMMA5 | 254                                            |
| Unified, 3-phase | H3-Pro / P3-Pro                                                                                                                         | 251 (37633–37699 are left out, see issue #692) |
| Unified, 1-phase | KH, H1-G2, AC1-G2, P1, EVO                                                                                                              | 218                                            |
| Not offered      | H1 / AC1 / AIO-H1 / AIO-AC1 (G1 and LAN), AIO-H3, Kuara H3, SK-HWR, STAR-H3, Solavita, Atronix                                          | —                                              |

Model names follow FoxESS' own documentation: the P3-S series (P3-5.0-SH … P3-15.0-SH, P3-10.0-SH1) shares
its manual with the H3-Smart / H3-M and uses the H3-Smart profile; the P3 Pro (P3-Pro-15.0 … 30.0) uses the
H3-Pro profile. The commercial P3 Plus (P3-50-Plus … P3-125-Plus) is not supported by this integration.

If your model is not offered but you believe its firmware supports the documented map, please say so in
your report.

## Safety

- The unified map **only reads**: none of its entities can change an inverter setting. Only a
  `foxess_modbus.write_registers` service call you make yourself writes anything, so don't call it
  while testing unless you know the register.
- **Use only one Modbus client per inverter.** Do not run another Modbus tool (Node-RED, modbus-cli,
  EVCC, a second HA instance…) against the same adapter while testing. Some firmware answers one
  request late. Two clients then receive each other's answers, which corrupts both.
- This test build also contains a workaround for inverters that answer one request behind (seen on H3
  Manager 1.93+). It is active for all models: every answer is checked to belong to its request, and
  unconfirmed answers are discarded rather than used. You may see a few extra requests per poll in the
  debug log. That is expected.

## Install the test build

1. Make a backup of your Home Assistant configuration (or at least of `config/custom_components/foxess_modbus`).
2. Copy the integration folder from this branch into `config/custom_components/foxess_modbus`,
   replacing the existing one.
3. Restart Home Assistant.
4. Check **Settings → Devices & services → FoxESS - Modbus**. The integration should load as before, with
   the switch still off.

The manifest version of the test build contains `unified`, for example
`1.16.0b2+pr1253.pr1261.pr1260.pr1234.lagfix2.newmap4.rw.unified2.quickfix1.custom`.

## Test procedure

**1. Record the baseline (switch off).**

- Note your **model**, the **Master / Slave / Manager** firmware versions (FoxESS app → device → firmware),
  and your **adapter** (e.g. Waveshare RS485-to-Ethernet, USB-RS485, the inverter's LAN port).
- Take a screenshot of the device page, or write down current values. At minimum, record PV power,
  grid/meter power, battery SoC, battery power and current, load power, and today's and total energy.

**2. Turn on debug logging.**

Either use **Settings → Devices & services → FoxESS - Modbus → ⋮ → Enable debug logging**, or add this to
`configuration.yaml` and restart:

```yaml
logger:
  default: warning
  logs:
    custom_components.foxess_modbus: debug
```

**3. Switch to the unified map.**

Go to Advanced options, tick _EXPERIMENTAL: use the unified FoxESS Modbus map (V1.05.04.00)_, and save.

**4. Let it run for at least 15 minutes.** A day is better, so that the energy counters and battery
charge/discharge phases are covered.

**5. Look at the results.**

- **Repairs:** does _"Invalid registers detected"_ appear under Settings → Repairs? Note the listed
  registers. These are addresses your inverter rejects, which is exactly the information we need.
- **Entities:** compare the values with your baseline and with the FoxESS app (see [What to check](#what-to-check)).
  Many entities are created **disabled**. Enable the ones you can judge, for example BMS cell voltages
  and temperatures, meter per-phase values, and EPS values.
- **Optional:** also enable _Create raw register entities_ in Advanced options. This adds
  developer entities for registers whose meaning is not confirmed yet, plus candidates such as ambient
  temperature (39142). They are created disabled. Enable the ones you want to compare.

**6. Download the log.** Use Settings → System → Logs → _Download full log_, or the file produced when
you disable debug logging. Search it for `foxess_modbus`.

**7. Report** (see [Reporting](#reporting)), then switch back or keep testing.

## What to check

For each item, compare with the FoxESS app or the normal map (baseline). **Sign conventions matter**: say
whether a value has the right magnitude but the wrong sign.

| Area                 | Entities (keys)                                                                                                                                | Look for                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Versions             | `master_version`, `slave_version`, `manager_version`                                                                                           | Must match the app exactly (36001 and 36002 are read as decimal, 36003 as hex digits) |
| Inverter state       | `inverter_state`                                                                                                                               | On Grid / Off Grid / Standby / Fault, as expected                                     |
| Faults               | `inverter_fault_code`                                                                                                                          | Normally empty; report anything unexpected                                            |
| PV                   | `pv1_voltage`, `pv1_current`, `pv1_power`, `pv2_*`, `pv3_*`, `reg_39118_total_pv_input_power`                                                  | Per string and total, vs app                                                          |
| Grid / meter         | `grid_ct_R`/`S`/`T`, `feed_in*`, `grid_consumption*`, `grid_voltage_*`, `rfreq`                                                                | Direction (import vs export), magnitude                                               |
| Load                 | `load_power`, `load_power_R`/`S`/`T`                                                                                                           | vs app "load"                                                                         |
| Battery              | `battery_soc`, `bat_current`, `batvolt`, `battery_charge`/`battery_discharge`, `invbatpower`                                                   | Sign while charging vs discharging                                                    |
| BMS                  | `battery_temp`, `battery_soh`, `bms_cell_temp_high`, `bms_cell_temp_low`, `bms_cell_mv_high`, `bms_cell_mv_low`, `bms_kwh_remaining`           | Plausible values, vs app/BMS                                                          |
| Energy               | `solar_energy_total`, `solar_energy_today`, `feed_in_energy_*`, `grid_consumption_energy_*`, `battery_charge_total`, `battery_charge_today`, … | Totals match the app, today's values reset at midnight                                |
| EPS                  | `eps_power_*`, `eps_rvolt_*`, `eps_rcurrent_*`, `eps_frequency`                                                                                | Only meaningful if you use EPS                                                        |
| Settings (read-only) | `max_charge_current`, `max_discharge_current`, `min_soc`, `max_soc`, `min_soc_on_grid`, `export_power_limit`                                   | Must match the values set in the app                                                  |

The complete list, including which entities start disabled, is in [unified-map-entities.md](unified-map-entities.md).

## Reporting

Please open an issue or comment in the testing discussion, using this template:

```markdown
### Unified map test report

- Model (as shown in the integration):
- Firmware (app): Master … / Slave … / Manager …
- Adapter / connection:
- Test build version (manifest):
- Duration of the test:

**Loaded without errors?** yes / no (paste the error)

**"Invalid registers detected" repair?** no / yes: <registers listed>

## **Wrong or implausible values** (key – unified value – expected value / app value – note):

## **Correct values** (short list of what you checked and was right):

**Versions shown** (master / slave / manager) vs app:

## **Anything that worked on the normal map but is missing on the unified map:**

**Log excerpt** (lines containing `foxess_modbus`; please remove your IP/serial if you wish):
```

Most useful are:

- the list of **invalid registers**;
- **wrong values**, with the expected value;
- whether the **version numbers** match the app. The encoding (decimal or hex) may differ between families.

## Going back

Untick the switch in Advanced options and save. The integration reloads with your model's normal map and
your entities come back.

To remove the test build entirely, restore your backup of `custom_components/foxess_modbus`, or reinstall
the release version through HACS, and restart.

## Known limitations and open questions

- **Read-only on purpose.** The writable registers of the new map (46607/46608 current limits, 46609–46611
  SoC limits, 49203 work mode, 46001+ remote control, …) have family-specific ranges. For example,
  46607/46608 are KH [0, 50] A and H1 [0, 40] A. These will be enabled per family once reads are
  confirmed.
- **Only confirmed on one H3** (Manager 1.95). Including H3 Manager 1.80–1.92 and the AC3 is an assumption.
- **Version decoding** (36001 decimal, 36002 decimal, 36003 hex) was confirmed on that H3 only.
- **Ambient temperature:** no documented register. 39142 is only a _developer_ candidate, and it reads 0 on
  the H3.
- **BMS max charge current:** no documented register. 37615 is a _developer_ candidate.
- **Inverter state:** "Off Grid" relies on bit 0 of _Status 3_ (39065–39066, 32 bits). The document doesn't
  say which of the two words holds bit 0, so both are checked. Off-grid and fault states have not been
  observed yet.
- **PV strings:** PV1–PV3 are included (39070–39075, 39279–39284). PV3 was taken over from the H3-Smart /
  KH / EVO definitions and is 0 on the two-string reference H3. PV4 (documented at 39076/39077,
  39285–39286) is not included yet. The total PV power (39118) is included.
- **Single-phase keys** end in `_R` (e.g. `grid_voltage_R`), unlike the family's normal keys.
  Dashboards and automations that use the normal keys need adjusting while testing.
- **Charge periods / time groups** are not available on the unified map yet (48014+ are only shown as
  read-only decoded sensors).
- The document's supported-model table (chapter 1.1) is empty, so which firmware supports the map is not
  documented. Your firmware versions in the report help to fill this gap.

## Technical notes

- Selecting the map: per inverter option `experimental_unified_map`. `Inv.UNIFIED_1PH` / `Inv.UNIFIED_3PH` are
  chosen from the family of the model's latest firmware, and are not part of `Inv.ALL`, so no existing
  entity description picks them up by accident.
- Entities: every read-only H3 (Manager 1.93+) entity whose registers are all in the new map. Taken over
  from the H3-Smart definitions, whose registers are the documented ones: the fault code (39067–39069,
  decoded like the H3-Pro / H3-Smart / KH 1.33+) and PV3. The PV energy integrations are included when
  their PV power source is on the map.
- Invalid ranges, never read across:

  - **measured on the H3:** 39185–39199, 39422–39424, 39633–39641, 45005–45008, 46008–46017,
    49184–49201, 49205, 49213–49220, 49231, 49250–49252, 53399–53416;
  - **plus the family's own known ranges within the new map:** H3-Pro 37633–37699, and H3-Smart
    individual reads of 37609–37620 and 37632–37636.

  An entity overlapping these ranges is not created for that family. Registers that answer
  _IllegalAddress_ at runtime are excluded automatically and listed in the repair notice.

- Measured on the H3, with 254 entities and a read-only full poll: the default entities take 13 Modbus
  exchanges in 0.85 s; with all entities, including developer ones, 26 exchanges in 1.8 s; no errors.
