# FoxESS Modbus test build: summary

**Build:** `1.16.0b2+pr1253.pr1261.pr1260.pr1234.lagfix2.newmap4.rw.unified2.quickfix1.custom`, based on upstream **v1.16.0b2**.
**Date:** 2026-09-30.

**Tested on:**

|                 |                                                                    |
| --------------- | ------------------------------------------------------------------ |
| Inverter        | FoxESS **H3-5.0-E** (three-phase hybrid, 2 PV strings)             |
| Firmware        | **Master 2.23**, **Slave 1.03**, **Manager 1.95**                  |
| Battery         | BMS master 1.013                                                   |
| Connection      | RS485 → Modbus TCP gateway (ESP32, eModbus), unit id 247, 9600 8N1 |
| Reference meter | HomeWizard P1, for the grid values                                 |

---

## 1. Upstream pull requests included

| PR                                                               | Title                                                                                           | What it brings                                                                                                                                                                                         | Status in this build                                                                                                               |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| [#1253](https://github.com/nathanmarlor/foxess_modbus/pull/1253) | Support H3 Manager >= 1.93 (Master 2.23): repair frames missing the unit id, add H3_193 profile | Repairs response frames without the unit id; adds `Inv.H3_193` for Manager 1.93+, whose battery charge/discharge today registers (32005/32008) hold the total mod 65536, so it drops those two sensors | Included. The H3_193 profile is the base of the port in section 3; the two battery-today sensors are back, from the new map.       |
| [#1261](https://github.com/nathanmarlor/foxess_modbus/pull/1261) | Fix H3 load power registers                                                                     | H3 load power from 31127 / 31129 / 31131 / 31133                                                                                                                                                       | Included for H3 before Manager 1.93. On Manager 1.93+ it is superseded by the new-map 39219–39226, verified against the phase sum. |
| [#1260](https://github.com/nathanmarlor/foxess_modbus/pull/1260) | Fix vendored pymodbus import on concurrent module changes                                       | Python 3.14 compatibility of the vendored pymodbus import                                                                                                                                              | Included                                                                                                                           |
| [#1234](https://github.com/nathanmarlor/foxess_modbus/pull/1234) | Fix H3 Smart model detection and PV Power unknown state                                         | Case-insensitive Smart suffix; LambdaSensors created after their source sensors                                                                                                                        | Included; regression tests cover case variants, profile ordering and a renamed PV source                                           |

**Not included:**

- [#949](https://github.com/nathanmarlor/foxess_modbus/pull/949) (H3 fixes package, WIP). It would remove remote control on H3 Manager 1.93+.
- Other open PRs for other families, e.g. #1238, #1245 and #1248.

Note for #1253: its version boundary is `Version(1, 92)`, while the change it describes starts at 1.93. In
the options this shows up as "1.92 and higher". It doesn't affect a 1.95 inverter, but it is worth checking
with the PR author.

## 2. Further fixes and changes in this build

- **Device-registry API compatibility (#1262).** Service controller lookup uses `registry.async_get(device_id)`
  instead of the deprecated `registry.devices.get(device_id)`. Device-ID, friendly-name and error paths are tested.
- **Lagged-response workaround.** Manager 1.93+ was seen answering every request with the answer to the
  _previous_ request, until some writes; it may come back.
  - Every answer is checked to belong to its request. A single register, or an exception, needs two
    agreeing answers. When no answer is accepted, the read or write fails instead of returning an
    unconfirmed value.
  - Write confirmations are checked for address and value (FC06) or address and count (FC16).
- **Pipelined polling.** Ranges are sent back to back:

  - probe pairs mark the start and the end;
  - no two neighbouring requests have the same length;
  - anything uncertain is re-read one range at a time.

  A full H3 poll takes 16 exchanges in about 1.0 s, against 20 exchanges in 1.3–1.8 s when reading one
  range at a time. Two bugs found in review were fixed, and the fix passes 35 176 simulated lag-switch and
  heartbeat scenarios with no wrong value.

- **FC06-only writes** for 44002–44003 and 44007–44013 on H3 Manager 1.93+.
- **Local H3 additions** kept from the previous custom build: Balance Mode, BMS Max Current and Export Power
  Limit control. These are ported to the new map on 1.93+, see section 3.
- **"PV Power" on H3 Manager 1.93+ is read from the inverter** (total PV input power, 39118–39119) instead of
  being computed as PV1 + PV2. The entity (`pv_power_now`) is unchanged.

## 3. Port to "Modbus definition (V1.05.04.00)" (H3 Manager 1.93+)

On Manager 1.93+ the H3 profile (`Inv.H3_193`) now reads the **documented new register map** (36xxx–39xxx,
45xxx–49xxx) wherever a register for the same value exists. Each moved value was checked live against its
legacy register first.

| Group                            | Count   | Content                                                                                                                                                                                                                                                                          |
| -------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Moved to the new register (read) | 61      | PV, grid/meter per phase, inverter per phase, load, EPS (with corrected R/S/T phase mapping), battery (SoC, voltage, current, power, temperature, SoH), BMS cells, all energy counters (including battery charge/discharge today, which the legacy map reports wrongly on 1.93+) |
| Versions                         | 3       | Master 36001 (decimal), Slave 36002 (decimal), Manager 36003 (hex). The legacy 30016–30018 hold serial number characters on this firmware.                                                                                                                                       |
| Writable settings moved          | 6 + 2   | Max charge/discharge current 46607/46608, min SoC 46609, max SoC 46610, min SoC on grid 46611, export limit 46616–46617; work mode 49203, balance mode 46614                                                                                                                     |
| Remote control moved             | 1       | 46001–46004 (enable, timeout, active power), plus the new-map battery, work mode and limit registers                                                                                                                                                                             |
| Inverter state                   | 1       | Decoded from Status 1 / Status 3 (39063, 39065–39066). Replaces the raw state code 31041.                                                                                                                                                                                        |
| Decoded text entities            | 9       | BMS and protocol version, EPS frequency and output mode, grid standard (98 codes), meter/CT type, date/time, time group 1 SoC                                                                                                                                                    |
| Further documented entities      | 64 + 20 | Named new-map sensors, plus H3-Smart definitions that answer correctly on the H3 (disabled by default)                                                                                                                                                                           |
| Developer entities               | 18      | New-map counterparts of the values kept on legacy registers, for comparison over time                                                                                                                                                                                            |
| Raw entities                     | 48      | Registers whose meaning isn't confirmed yet (developer option, disabled)                                                                                                                                                                                                         |
| Still on legacy registers        | 3       | Ambient temperature 31033 (no documented register), BMS max current 31039 (undocumented 37615 candidate), fault codes 31044–31051 (bit mapping of 39067–39069 not confirmed)                                                                                                     |

Invalid ranges were measured address by address: 39185–39199, 39422–39424, 39633–39641, 45005–45008,
46008–46017, 49184–49201, 49205, 49213–49220, 49231, 49250–49252 and 53399–53416. No read spans them.

## 4. EXPERIMENTAL: unified map for other families

There is an opt-in, read-only switch in _Advanced options_: "EXPERIMENTAL: use the unified FoxESS Modbus map
(V1.05.04.00)". It is offered for 13 models:

- **3-phase, 235 entities:** H3, AC3, H3-Smart / H3-M, P3-S (P3-x.x-SH), SK-HWR-Smart, Enpal I-X and 1KOMMA5;
  H3-Pro / P3-Pro get 232.
- **1-phase, 201 entities:** KH, H1-G2, AC1-G2, P1 and EVO.

With the switch off, every model and firmware version keeps a byte-identical entity set. **So far it has only
been tested on the H3 above.** Testing guide: [unified-map-testing.md](unified-map-testing.md). Entity list:
[unified-map-entities.md](unified-map-entities.md).

## 5. Tests on the H3 (Master 2.23 / Manager 1.95)

All reads were read-only, with the HA integration disabled and a 12 s check that no other client was on the bus.
Writes were only made with the owner's explicit approval.

| Time (2026-09-30) | Test                                                                                                           | Result                                                                                                                                                                 |
| ----------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| morning           | Root cause of the failed setup / garbage values                                                                | Inverter answers one request behind (content-verified, including exception replies). The workaround was verified live.                                                 |
| 12:11             | Scan of all documented new-map registers                                                                       | 312 of 331 answer; 58 matched the legacy map                                                                                                                           |
| 12:15             | Grid values vs HomeWizard P1                                                                                   | Per-phase power within about 6 W, voltage within 0.2–0.4 V                                                                                                             |
| 14:28–14:30       | Independent full verification of the build                                                                     | 237 new-map entities bit-exact with the PDF; all controller read ranges error-free; invalid ranges and their neighbours confirmed                                      |
| 14:33             | Writable settings at legacy and new addresses                                                                  | All 11 pairs identical                                                                                                                                                 |
| 14:46             | Same-value writes to the new writable registers                                                                | Accepted: 46607–46611, 49203, 46616–46617 (FC16). Rejected: balance mode 2 at 46614 (IllegalValue; the legacy register rejects it too, it can only be set in the app). |
| 14:47             | Remote control (46001–46004): enable, setpoint, restore                                                        | Worked. **Side effect:** max charge/discharge current changed from 15 A to 0 A afterwards (cause not proven, restored in the app). See open items.                     |
| 15:38             | Pipelined polling after the review fixes                                                                       | Full H3 cycle 16 exchanges / 1.08 s; no re-read; no error; no range assigned to a wrong address compared with one-range-at-a-time reads                                |
| 15:52             | 10 legacy → new swaps (battery voltage, current, temperature, SoH, BMS cells, remaining energy, EPS frequency) | All equal over three rounds, with 6 A battery current and the same sign                                                                                                |
| 16:05             | Inverter state                                                                                                 | Status 1 = 0x0004 (Operation) while legacy 31041 = 2 (On Grid) → "On Grid"                                                                                             |
| 16:09             | Developer comparison registers                                                                                 | 37615 = 31039 = 14 A; 39142 = 0 vs 31033 = 49 °C; all fault words 0                                                                                                    |
| 19:4x             | Unified map, full read-only cycle                                                                              | 235 entities, no legacy address; 13 exchanges / 0.87 s; 0 errors                                                                                                       |

**Offline checks:**

- all 35 model/firmware combinations serialize without an invalid address or duplicate key (3253 entities);
- 162 numeric H3 entities match the PDF in address, word order, sign and scale;
- controller read ranges pass in 20 variants;
- 10 frame-repair tests pass;
- the unified map passes on all 13 offered models;
- the patch reproduces the build exactly on a clean v1.16.0b2.
- Python 3.13 / Home Assistant 2025.8.0: 82 pytest tests and 37 snapshots pass; all pre-commit hooks pass.
  The 15 new regression cases cover the Smart model suffix, dependent sensor creation and device lookup.
  A further 28 cases cover entity nomenclature, BMS versus inverter inputs, and preservation of non-name fields.
  All 37 snapshots differ from the pre-naming build in names only; identifiers, values, units and controls are unchanged.
  The complete display-name mapping is in [entity-name-changes.md](entity-name-changes.md).

**Home Assistant:** an earlier stage of this build (the lag workaround) ran in Home Assistant on the H3.
The current build has not been run in Home Assistant yet, because the integration was kept disabled during the
register tests. In particular, the new options switch still needs to be checked in the UI.

## 6. Open items

- **Force charge / force discharge:** see the 14:47 side effect. Until it is understood, the build still
  offers these modes; a guard (hide, or put behind an option) is pending a decision.
- The #1253 version boundary (1.92 vs 1.93).
- The unified map is read-only; the writable ranges differ per family (e.g. 46607/46608: KH 0–50 A, H1 0–40 A).
- PV4 (39076/39077, 39285–39286) is not included yet; PV1–PV3 are.
- Off-grid and fault states have not been observed yet (Status 3 word order is undocumented, so both words
  are checked).
- The energy counters vs the P1 meter over more than an hour: net export minus import only, because the two
  meters balance the phases differently.
