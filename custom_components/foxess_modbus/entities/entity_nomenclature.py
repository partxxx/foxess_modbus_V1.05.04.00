"""Consistent display names without changing entity identifiers or register semantics."""

import re
from dataclasses import replace
from typing import Any
from typing import Iterable
from typing import cast

from homeassistant.helpers.entity import EntityDescription

from .entity_factory import EntityFactory
from .inverter_model_spec import ModbusAddressSpecBase

# Register-specific names take precedence over historical keys. In particular, 39423 is System SoC,
# although the existing EVO entity key is battery_soh. This does not change its value or identifier.
# Only registers whose meaning is the same for every entity reading them belong here: candidates are named by
# their developer key (EVO reads 39142 as its ambient temperature), and 39216 is the EPS T phase on the
# H3-Pro / H3-Smart (see #669).
_REGISTER_NAMES = {
    37003: "BMS1 BAT Master Version",
    37633: "BMS1 BAT Capacity Full Charge",
    37635: "BMS1 BAT Energy Nominal",
    39051: "PV String Count",
    39052: "MPPT Count",
    39053: "Inverter Power Rated",
    39055: "Inverter Active Power Max",
    39057: "Inverter Apparent Power Max",
    39059: "Inverter Reactive Power Export Max",
    39061: "Inverter Reactive Power Import Max",
    39118: "PV Power",
    39149: "Inverter Energy Generation Total",
    39151: "Inverter Energy Generation Today",
    39219: "Load R Power",
    39221: "Load S Power",
    39223: "Load T Power",
    39225: "Load Power",
    39270: "Inverter Apparent Power",
    39272: "Inverter R Frequency",
    39273: "Inverter S Frequency",
    39274: "Inverter T Frequency",
    39275: "Inverter Power Import Available",
    39277: "Inverter Power Export Available",
    39423: "System SoC",
    46002: "Inverter Remote Control Timeout",
    46003: "Inverter Active Power Setpoint",
    46005: "Inverter Reactive Power Setpoint",
    46007: "Inverter Remote Control Countdown",
    46018: "Inverter BAT Power Discharge Available",
    46020: "Inverter BAT Power Charge Available",
    46503: "Inverter BAT SoC Threshold",
    46504: "Inverter Power Export Peak Limit",
    46607: "Inverter BAT Current Charge Max",
    46608: "Inverter BAT Current Discharge Max",
    46609: "Inverter BAT SoC Min",
    46610: "Inverter BAT SoC Max",
    46611: "Inverter BAT SoC Min On Grid",
    46612: "EPS Frequency Setting",
    46613: "EPS Output Mode",
    46616: "Inverter Power Export Limit",
    46618: "Inverter Current Import Limit",
    46619: "Inverter Current Export Limit",
    46620: "Inverter BAT SoC Max From Grid",
    48015: "Time Group1 FC/FD SoC Candidate",
    48016: "Time Group1 FC/FD Power Candidate",
    49007: "Inverter Active Power Percentage",
    49008: "Inverter Active Power Dispatch Setpoint",
    49010: "Inverter Reactive Power Night",
    49136: "Grid Connection Power Limit",
    49207: "Meter1/CT1 Type",
    49221: "Inverter Display Brightness",
    49222: "Inverter Date Time",
    49230: "Load Power Idle Threshold",
    49248: "Meter Power Compensation",
    49249: "Inverter GFCI Current",
}

_KEY_NAMES = {
    "reg_37615_bms_max_current_candidate": "BMS1 BAT Current Charge Max",
    "reg_37616_bms_max_discharge_current": "BMS1 BAT Current Discharge Max",
    "reg_37613_bms_charge_voltage_max": "BMS1 BAT Voltage Charge Max",
    "reg_37614_bms_discharge_voltage_min": "BMS1 BAT Voltage Discharge Min",
    "reg_39142_ambtemp_candidate": "Inverter Ambient Temperature Candidate",
    "ambtemp": "Inverter Ambient Temperature",
    "balance_mode": "Inverter Balance Mode",
    "bms_charge_rate": "BMS BAT Current Charge Max",
    "bms_discharge_rate": "BMS BAT Current Discharge Max",
    "bms_cycle_count": "BMS BAT Cycle Count",
    "bms_max_current": "BMS BAT Current Max",
    "bms_watthours_total": "BMS BAT Energy Throughput Total",
    "export_power_limit": "Inverter Power Export Limit",
    "import_power_limit": "Inverter Power Import Limit",
    "force_charge_max_soc": "Inverter BAT SoC Force Charge Max",
    "force_charge_mode": "Inverter Remote Control Mode",
    "force_charge_power": "Inverter BAT Power Force Charge",
    "force_discharge_power": "Inverter BAT Power Force Discharge",
    "invtemp": "Inverter Temperature",
    "max_charge_current": "Inverter BAT Current Charge Max",
    "max_discharge_current": "Inverter BAT Current Discharge Max",
    "min_soc": "Inverter BAT SoC Min",
    "max_soc": "Inverter BAT SoC Max",
    "min_soc_on_grid": "Inverter BAT SoC Min On Grid",
    "work_mode": "Inverter Work Mode",
    "time_group_1_max_soc_from_grid": "Time Group1 SoC Max From Grid",
    "time_group_1_min_soc_on_grid": "Time Group1 SoC Min On Grid",
}

_BMS_QUANTITIES = {
    "battery_soc": "SoC",
    "battery_soh": "SoH",
    "battery_temp": "Temperature",
    "bms_cell_mv_high": "Cell Voltage Max",
    "bms_cell_mv_low": "Cell Voltage Min",
    "bms_cell_temp_high": "Cell Temperature Max",
    "bms_cell_temp_low": "Cell Temperature Min",
    "bms_kwh_remaining": "Energy Remaining",
}


_BMS_ELECTRONICS_TEMPERATURE = (37611, 38309, 31037)


def _battery_name(key: str, address: int | None) -> str | None:
    """BMS indices and inverter BAT input indices are independent namespaces."""
    match = re.fullmatch(r"(.+?)(?:_([12]))?", key)
    assert match is not None
    base, index = match.groups()
    bms_index = "1" if address is not None and 37002 <= address <= 37636 else None
    if address is not None and 37700 <= address <= 38334:
        bms_index = "2"
    if base == "battery_temp" and address in _BMS_ELECTRONICS_TEMPERATURE:
        # The BMS's own (electronics) temperature, not a cell temperature: "BMS1 Ambient Temperature" in the Modbus
        # definition; the legacy H3 31037 reads the same value as 37611 (checked live)
        return f"BMS{bms_index or index or ''} Temperature"
    if base in _BMS_QUANTITIES:
        return f"BMS{bms_index or index or ''} BAT {_BMS_QUANTITIES[base]}"

    quantities = {"batvolt": "Voltage", "bat_current": "Current"}
    if base in quantities:
        if bms_index or index:
            return f"BMS{bms_index or index} BAT {quantities[base]}"
        if address in (39227, 39228):
            return f"Inverter BAT1 {quantities[base]}"
        if address in (31034, 31035):
            # Legacy H3 inverter-side readings were compared with the new BAT1 measurements live.
            return f"Inverter BAT {quantities[base]}"
        return f"BAT {quantities[base]} Source Unconfirmed"

    quantities = {"invbatvolt": "Voltage", "invbatcurrent": "Current", "invbatpower": "Power"}
    if base in quantities:
        if address in (39227, 39228, 39230):
            index = "1"
        elif address in (39232, 39233, 39235):
            index = "2"
        elif address == 39237:
            index = None
        return f"Inverter BAT{index or ''} {quantities[base]}"

    if base in ("battery_charge", "battery_discharge"):
        if address == 39230:
            index = "1"
        elif address == 39235:
            index = "2"
        elif address == 39237:
            index = None
        direction = "Charge" if base == "battery_charge" else "Discharge"
        return f"Inverter BAT{index or ''} Power {direction}"
    match = re.fullmatch(r"battery_(charge|discharge)_(today|total)", key)
    if match:
        direction, period = match.groups()
        return f"Inverter BAT Energy {direction.title()} {period.title()}"
    return None


def entity_display_name(key: str, name: str, address: int | None = None) -> str:
    """Return a display name; never change identifiers, units, scaling or values."""
    for prefix, suffix in (("legacy_", " Legacy"), ("newmap_", " New Map")):
        if key.startswith(prefix):  # register palette twin: named like the entity it mirrors
            return entity_display_name(key.removeprefix(prefix), name, address) + suffix
    if key.startswith("register_"):
        return name.removesuffix(" raw") + " Raw" if name.endswith(" raw") else name
    if key.startswith("reg_") and "legacy_fault_word" in key:
        return f"Inverter Legacy Fault Word {address} Raw"
    if key.startswith("reg_") and "_alarm_" in key:
        return f"Inverter Alarm{key.rsplit('_', 1)[1]} Raw"
    if key.startswith("reg_") and "_bms1_fault" in key:
        return f"BMS1 BAT Fault{key.rsplit('fault', 1)[1]} Raw"
    if address in _REGISTER_NAMES:
        return _REGISTER_NAMES[address]
    if key in _KEY_NAMES:
        return _KEY_NAMES[key]
    battery_name = _battery_name(key, address)
    if battery_name:
        return battery_name

    match = re.fullmatch(r"(master|slave|manager)_version", key)
    if match:
        return f"Inverter {match[1].title()} Version"
    match = re.fullmatch(r"pv([1-6])_energy_total", key)
    if match:
        return f"PV{match[1]} Energy Total"
    match = re.fullmatch(r"(solar_energy|total_yield|input_energy)_(today|total)", key)
    if match:
        energy = {
            "solar_energy": "PV Energy",
            "total_yield": "Inverter Energy Yield",
            "input_energy": "Inverter Energy Input",
        }[match[1]]
        return f"{energy} {match[2].title()}"
    if key == "load_power_total":
        return "Load Energy Total"
    match = re.fullmatch(r"(feed_in|grid_consumption)(?:_energy_(today|total)|_([RST]))?", key)
    if match:
        subject, period, phase = match.groups()
        direction = "Export" if subject == "feed_in" else "Import"
        if period:
            return f"Grid Energy {direction} {period.title()}"
        return " ".join(x for x in ("Grid", phase, "Power", direction) if x)
    match = re.fullmatch(r"(grid_ct(?:_apparent|_reactive|_pf)?|ct2_meter)(?:_([RST]))?", key)
    if match:
        subject, phase = match.groups()
        quantity = {
            "grid_ct_apparent": "Apparent Power",
            "grid_ct_reactive": "Reactive Power",
            "grid_ct_pf": "Power Factor",
        }.get(subject, "Power")
        return " ".join(x for x in ("Meter", "CT2" if subject == "ct2_meter" else "CT1", phase, quantity) if x)
    match = re.fullmatch(r"time_period_([12])_(.+)", key)
    if match:
        quantity = {
            "start": "Start",
            "end": "End",
            "enable_force_charge": "Force Charge Enabled",
            "enable_charge_from_grid": "Charge From Grid Enabled",
        }[match[2]]
        return f"Time Period{match[1]} {quantity}"

    # Remaining documented names: remove address decoration, expand inconsistent abbreviations,
    # and move phase labels to the same position, ahead of the measured quantity.
    name = re.sub(r"\s*\(\d{5}\)$", "", name)
    name = name.replace("_", " ")
    name = re.sub(r"\bTemp\b\.?", "Temperature", name)
    name = re.sub(r"\bFreq\b", "Frequency", name)
    name = re.sub(r"\bMinimum\b", "Min", name)
    name = re.sub(r"\bMaximum\b", "Max", name)
    name = name.replace("Grid CT1", "Meter CT1").replace(" Phase", "").replace(" Combined", "")
    name = name.replace("(Reactive)", "Reactive").replace("(Apparent)", "Apparent")
    name = name.replace("Power Reactive", "Reactive Power").replace("Power Apparent", "Apparent Power")
    name = re.sub(r"\b(Reactive|Apparent)$", r"\1 Power", name)
    name = re.sub(r"^(Inverter|Grid|EPS|Load|Meter CT[12]) (.+) ([RST])$", r"\1 \3 \2", name)
    return name


def apply_entity_nomenclature(entities: Iterable[EntityFactory]) -> list[EntityFactory]:
    """Split address specifications only when the measured source requires different names.

    The original key, supported model/register-type pairs and every non-name field remain unchanged.
    This lets the same historical key be named BMS1 BAT Voltage on one map and Inverter BAT1 Voltage
    on another without making the entity mixin or HA registry guess its source at runtime.
    """
    result: list[EntityFactory] = []
    for factory in entities:
        description = cast(EntityDescription, factory)
        assert isinstance(description.name, str), description.key
        field = next((field for field in ("addresses", "address") if getattr(factory, field, None)), None)
        if field is None:
            result.append(replace(cast(Any, factory), name=entity_display_name(description.key, description.name)))
            continue
        groups: dict[str, list[ModbusAddressSpecBase]] = {}
        for spec in getattr(factory, field):
            assert isinstance(spec, ModbusAddressSpecBase), description.key
            # A spec can have input and holding addresses. Preserve its register-type support even if
            # those maps need different display names.
            for register_type, addresses in spec._addresses.items():  # noqa: SLF001
                address = min(addresses) if addresses else None
                display_name = entity_display_name(description.key, description.name, address)
                groups.setdefault(display_name, []).append(
                    ModbusAddressSpecBase({register_type: addresses}, spec._models)  # noqa: SLF001
                )
        for display_name, specs in groups.items():
            result.append(replace(cast(Any, factory), name=display_name, **{field: specs}))
    return result
