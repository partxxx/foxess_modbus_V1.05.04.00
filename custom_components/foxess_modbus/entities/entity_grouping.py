"""Groups entities as sensors, diagnostics or experimental, without changing keys, unique ids or values.

- Sensor: a physically measured quantity (SoC, SoH, voltage, current, power, energy, temperature, frequency, power
  factor, time) whose meaning is proven: it matches the FoxESS Cloud API, is physically consistent with proven
  entities (e.g. S = U * I, PF = P / S), or equals a known value.
- Diagnostic: everything that isn't a measured quantity: states, statuses and fault codes, settings without a
  control (read-backs of writable registers), limits, versions, names and types (nameplate values).
- Configuration: the writable device settings (numbers and selects). Their state is the value read back from the
  register, so a separate read-back sensor with the same key is dropped for the models which have the control.
  Remote control (force charge / discharge) stays in Controls: those are actions, not settings.
- Experimental: unnamed (raw) registers and registers whose meaning isn't proven yet. They are enabled by default,
  but belong to a separate "Experimental" device next to the inverter (see ModbusEntityMixin.device_info).

Evidence (H3-5.0-E, Manager 1.95, night of 2026-09-30): ha_export_20260930_1000/API_OSSZEVETES.md in the
foxx-modbus workspace.
"""

import copy
from dataclasses import replace
from typing import Any
from typing import Iterable

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import EntityCategory

from ..common.types import Inv
from .entity_factory import EntityFactory

DIAGNOSTIC_KEYS = frozenset(
    {
        # Versions
        "master_version",
        "slave_version",
        "manager_version",
        "bms1_master_version",
        "modbus_protocol_version",
        # States and fault codes
        "connection_status",
        "inverter_state",
        "state_code",
        "inverter_fault_code",
        "reg_39067_alarm_1",
        "reg_39068_alarm_2",
        "reg_39069_alarm_3",
        "reg_37626_bms1_fault1",
        "reg_37627_bms1_fault2",
        "reg_37628_bms1_fault3",
        "reg_37629_bms1_fault4",
        "reg_37630_bms1_fault5",
        "reg_37631_bms1_fault6",
        "reg_31044_legacy_fault_word",
        "reg_31045_legacy_fault_word",
        "reg_31047_legacy_fault_word",
        "reg_31048_legacy_fault_word",
        "reg_31049_legacy_fault_word",
        "reg_31050_legacy_fault_word",
        "reg_31051_legacy_fault_word",
        # Nameplate
        "reg_39051_number_of_strings",
        "reg_39052_number_of_mppts",
        "reg_39053_rated_power_pn",
        "reg_39055_maximum_active_power_pmax",
        "reg_39057_max_apparent_power_smax",
        "reg_39059_max_reactive_power_fed_qmax",
        "reg_39061_max_reactive_power_absorbed_qmax",
        "reg_37635_bms1_design_energy",
        # BMS limits (37615 / 37616 = the API's maxChargeCurrent / maxDischargeCurrent)
        "bms_max_current",
        "reg_37615_bms_max_current_candidate",
        "reg_37616_bms_max_discharge_current",
        # Read-backs of writable registers
        "max_charge_current",
        "max_discharge_current",
        "min_soc",
        "max_soc",
        "min_soc_on_grid",
        "export_power_limit",
        "import_power_limit",
        "time_group_1_max_soc_from_grid",
        "time_group_1_min_soc_on_grid",
        "eps_frequency_select",
        "eps_output_mode",
        "grid_standard",
        "meter1_ct1_type",
        "reg_46002_remote_timeout_set",
        "reg_46003_control_active_power",
        "reg_46005_control_reactive_power",
        "reg_46007_remote_timeout_countdown",
        "reg_46503_threshold_soc",
        "reg_46504_export_peak_limit",
        "reg_46618_import_current_limit",
        "reg_46619_export_current_limit",
        "reg_46620_maximum_soc_from_grid",
        "reg_49007_active_power_percentage",
        "reg_49008_fixed_active_power_dispatch",
        "reg_49010_night_reactive_power",
        "reg_49136_grid_point_power_limit",
        "reg_49221_brightness_level",
        "reg_49230_idle_loadpower_threshold",
        "reg_49243_k1_power_ratio",
        "reg_49244_k2_power_ratio",
        "reg_49245_k3_power_ratio",
        "reg_49246_k4_power_ratio",
        "reg_49248_meter_compensation",
    }
)

# Writable device settings: numbers and selects which belong to the Configuration group
CONFIG_KEYS = frozenset(
    {
        "max_charge_current",
        "max_discharge_current",
        "min_soc",
        "max_soc",
        "min_soc_on_grid",
        "export_power_limit",
        "import_power_limit",
        "work_mode",
        "balance_mode",
    }
)

# Diagnostic by kind, for every inverter family: versions, fault codes, states, charge period settings
_DIAGNOSTIC_CLASSES = frozenset(
    {
        "ModbusVersionSensorDescription",
        "ModbusFaultSensorDescription",
        "ModbusInverterStateSensorDescription",
        "ModbusG2InverterStateSensorDescription",
        "ModbusChargePeriodStartEndSensorDescription",
    }
)

# Discovered measurements which were off by default and are now proven
_PROMOTED_KEYS = frozenset({"inverter_date_time"})

# Named, but the meaning isn't proven (always 0, empty in the firmware, or no second source agrees yet)
EXPERIMENTAL_KEYS = frozenset(
    {
        "reg_39142_ambtemp_candidate",
        "reg_39216_eps_combined_power",
        "reg_39275_available_import_power",
        "reg_39277_available_export_power",
        "reg_48015_time_group_n_fc_fdsoc",
        "reg_48016_time_group_n_fc_fdpwr",
        "reg_46018_pwr_limit_bat_up",
        "reg_46020_pwr_limit_bat_dn",
        "reg_37633_bms1_fcc_capacity",
        "reg_49249_gfci_current",
        "reg_37613_bms_charge_voltage_max",
        "reg_37614_bms_discharge_voltage_min",
    }
)


PALETTE_PREFIXES = ("legacy_", "newmap_")


def is_palette(key: str) -> bool:
    """The other register (legacy or documented map) of an entity, shown next to it on the playground"""
    return key.startswith(PALETTE_PREFIXES)


def _base_key(key: str) -> str:
    for prefix in PALETTE_PREFIXES:
        key = key.removeprefix(prefix)
    return key


def is_experimental(key: str) -> bool:
    """Unnamed raw registers and named registers whose meaning isn't proven"""
    return key.startswith("register_") or key in EXPERIMENTAL_KEYS


def _is_discovered(key: str) -> bool:
    return key.startswith(("reg_", "register_", "time_group_1_"))


def is_diagnostic(description: Any) -> bool:
    return _base_key(description.key) in DIAGNOSTIC_KEYS or type(description).__name__ in _DIAGNOSTIC_CLASSES


def _grouped(description: Any) -> Any:
    key = description.key
    changes: dict[str, Any] = {}
    if is_diagnostic(description):
        changes["entity_category"] = EntityCategory.DIAGNOSTIC
    elif key in _PROMOTED_KEYS or is_experimental(key) or _is_discovered(key):
        # Experimental entities are grouped by their device; proven discovered ones are plain sensors
        changes["entity_category"] = None
    if (
        is_palette(key)
        or key in DIAGNOSTIC_KEYS
        or key in _PROMOTED_KEYS
        or is_experimental(key)
        or _is_discovered(key)
    ):
        # Discovered registers were off by default while unproven; they are live now, in their group
        changes["entity_registry_enabled_default"] = True
    return replace(description, **changes) if changes else description


_SPEC_FIELDS = ("addresses", "address")


def _models(description: Any) -> Inv:
    models = Inv(0)
    for field_name in _SPEC_FIELDS:
        for spec in getattr(description, field_name, None) or []:
            models |= getattr(spec, "_models", Inv(0))
    return models


def _without_models(description: Any, models: Inv) -> Any | None:
    """Copy of the description which no longer applies to the given models, or None if nothing is left"""
    changes = {}
    for field_name in _SPEC_FIELDS:
        specs = getattr(description, field_name, None)
        if not isinstance(specs, list) or not any(hasattr(spec, "_models") for spec in specs):
            continue
        kept = []
        for spec in specs:
            if spec._models & models:  # noqa: SLF001
                spec = copy.copy(spec)
                spec._models = spec._models & ~models  # noqa: SLF001
                if not spec._models:  # noqa: SLF001
                    continue
            kept.append(spec)
        if not kept:
            return None
        changes[field_name] = kept
    return replace(description, **changes) if changes else description


def apply_entity_grouping(entities: Iterable[EntityFactory]) -> list[EntityFactory]:
    """Group entities (category, default enablement); keys, unique ids and values are unchanged."""
    # hass type hints: mypy doesn't see the dataclass fields of the EntityDescriptions
    descriptions: list[Any] = list(entities)
    controlled: dict[str, Inv] = {}
    for description in descriptions:
        if not isinstance(description, SensorEntityDescription) and description.key in CONFIG_KEYS:
            controlled[description.key] = controlled.get(description.key, Inv(0)) | _models(description)
    result: list[EntityFactory] = []
    for description in descriptions:
        if isinstance(description, SensorEntityDescription):
            if description.key in controlled:
                # The control shows the read-back value itself
                description = _without_models(description, controlled[description.key])
                if description is None:
                    continue
            result.append(_grouped(description))
        elif description.key in CONFIG_KEYS:
            result.append(replace(description, entity_category=EntityCategory.CONFIG))
        else:
            result.append(description)
    return result
