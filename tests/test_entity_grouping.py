"""Sensors, diagnostics and the experimental device; keys and unique ids don't change."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.helpers import device_registry

from custom_components.foxess_modbus.common.types import Inv
from custom_components.foxess_modbus.common.types import RegisterType
from custom_components.foxess_modbus.const import DOMAIN
from custom_components.foxess_modbus.const import FRIENDLY_NAME
from custom_components.foxess_modbus.const import INVERTER_BASE
from custom_components.foxess_modbus.const import INVERTER_CONN
from custom_components.foxess_modbus.const import INVERTER_MODEL
from custom_components.foxess_modbus.entities.entity_descriptions import ENTITIES
from custom_components.foxess_modbus.entities.entity_grouping import CONFIG_KEYS
from custom_components.foxess_modbus.entities.entity_grouping import DIAGNOSTIC_KEYS
from custom_components.foxess_modbus.entities.entity_grouping import EXPERIMENTAL_KEYS
from custom_components.foxess_modbus.entities.entity_grouping import INTEGRATED_PV_ENERGY_KEYS
from custom_components.foxess_modbus.entities.entity_grouping import MODBUS_PV_ENERGY_KEY
from custom_components.foxess_modbus.entities.entity_grouping import is_diagnostic
from custom_components.foxess_modbus.entities.entity_grouping import is_experimental
from custom_components.foxess_modbus.entities.modbus_entity_mixin import ModbusEntityMixin
from custom_components.foxess_modbus.flow.flow_handler import FlowHandler
from custom_components.foxess_modbus.inverter_profiles import INVERTER_PROFILES
from custom_components.foxess_modbus.services import utils


def _h3_193() -> list[Any]:
    return [f for f in ENTITIES if f.serialize(Inv.H3_193, RegisterType.HOLDING) is not None]


def _all() -> list[Any]:
    return list(ENTITIES)


def _is_sensor(factory: Any) -> bool:
    return isinstance(factory, SensorEntityDescription)


def test_grouped_keys_exist() -> None:
    keys = {f.key for f in _all()}
    # connection_status is created by the platform; state_code is replaced by inverter_state on H3_193
    assert DIAGNOSTIC_KEYS - keys == {"connection_status"}
    assert {f.key for f in _h3_193()} >= EXPERIMENTAL_KEYS
    assert not DIAGNOSTIC_KEYS & EXPERIMENTAL_KEYS


def test_categories() -> None:
    for factory in _h3_193():
        key = factory.key
        if not isinstance(factory, SensorEntityDescription):
            # writable settings are Configuration; remote control (force charge / discharge) stays in Controls
            expected = EntityCategory.CONFIG if key in CONFIG_KEYS else None
            assert factory.entity_category == expected, key
        elif is_diagnostic(factory):
            assert factory.entity_category == EntityCategory.DIAGNOSTIC, key
        elif key.startswith(("reg_", "register_")):
            assert factory.entity_category is None, key
        if isinstance(factory, SensorEntityDescription) and (
            key in DIAGNOSTIC_KEYS or key.startswith(("reg_", "register_"))
        ):
            assert factory.entity_registry_enabled_default, key


def test_experimental_selection() -> None:
    raw = {f.key for f in _h3_193() if f.key.startswith("register_")}
    assert raw and all(is_experimental(key) for key in raw)
    assert not is_experimental("reg_37615_bms_max_current_candidate")  # proven: the API's maxChargeCurrent
    assert not is_experimental("reg_38832_grid_ct1_r_phase_apparent")  # proven: S = U * I
    assert is_experimental("reg_39142_ambtemp_candidate")
    assert is_experimental("reg_37613_bms_charge_voltage_max")  # BMS voltage limits: no second source yet
    assert is_experimental("reg_37614_bms_discharge_voltage_min")


def test_only_measured_quantities_are_sensors() -> None:
    by_key = {f.key: f for f in _h3_193() if isinstance(f, SensorEntityDescription)}
    for key in (
        "battery_soc",
        "battery_soh",
        "batvolt",
        "pv1_current",
        "load_power",
        "solar_energy_total",
        "invtemp",
        "inverter_date_time",
    ):
        assert by_key[key].entity_category is None, key
    for key in (
        "master_version",
        "inverter_state",
        "inverter_fault_code",
        "import_power_limit",
        "grid_standard",
        "meter1_ct1_type",
        "bms_max_current",
        "reg_39053_rated_power_pn",
        "reg_39067_alarm_1",
    ):
        assert by_key[key].entity_category == EntityCategory.DIAGNOSTIC, key
    assert by_key["inverter_date_time"].entity_registry_enabled_default


def _device(key: str) -> dict[str, Any]:
    entity = SimpleNamespace(
        entity_description=SimpleNamespace(key=key),
        _controller=SimpleNamespace(
            inverter_details={FRIENDLY_NAME: "inv", INVERTER_MODEL: "H3", INVERTER_CONN: "AUX"}
        ),
    )
    info: dict[str, Any] = ModbusEntityMixin.device_info.fget(entity)  # type: ignore[attr-defined]
    return info


def test_experimental_device() -> None:
    inverter = _device("pv1_power")
    experimental = _device("register_39134_raw")
    assert inverter["identifiers"] == {(DOMAIN, "H3", "AUX", "inv")}
    assert experimental["identifiers"] == {(DOMAIN, "H3", "AUX", "inv", "experimental")}
    assert experimental["via_device"] == (DOMAIN, "H3", "AUX", "inv")
    assert experimental["name"] == "FoxESS - Modbus (inv) Experimental"


def test_services_resolve_the_experimental_device(monkeypatch: pytest.MonkeyPatch) -> None:
    controller = MagicMock()
    controller.inverter_details = {FRIENDLY_NAME: "inv"}
    device = SimpleNamespace(identifiers=_device("register_39134_raw")["identifiers"])
    monkeypatch.setattr(
        device_registry, "async_get", lambda _hass: SimpleNamespace(async_get=Mock(return_value=device))
    )
    assert utils.get_controller_from_friendly_name_or_device_id("id", [controller], MagicMock()) is controller


def test_configuration_controls_replace_their_read_back_sensors() -> None:
    for inv in Inv:
        controls = {
            f.key
            for f in _all()
            if not isinstance(f, SensorEntityDescription)
            and f.key in CONFIG_KEYS
            and f.serialize(inv, RegisterType.HOLDING) is not None
        }
        sensors = {
            f.key
            for f in _all()
            if _is_sensor(f) and any(f.serialize(inv, register_type) is not None for register_type in RegisterType)
        }
        assert not controls & sensors, (inv, controls & sensors)
    h3 = {f.key for f in _h3_193() if not isinstance(f, SensorEntityDescription)}
    assert {"max_soc", "min_soc", "export_power_limit", "work_mode", "balance_mode"} <= h3


def test_bms_current_limits_are_live_diagnostics() -> None:
    by_key = {f.key: f for f in _h3_193()}
    for key in ("reg_37615_bms_max_current_candidate", "reg_37616_bms_max_discharge_current"):
        factory = by_key[key]
        assert factory.entity_category == EntityCategory.DIAGNOSTIC, key
        assert factory.entity_registry_enabled_default, key
        assert not getattr(factory, "raw", False), key  # not behind the raw register option


def test_pv_energy_is_read_where_the_inverter_counts_it() -> None:
    """Every inverter has exactly one PV energy source: its own counter, or else the energy integrated in HA"""
    keys = {MODBUS_PV_ENERGY_KEY, *INTEGRATED_PV_ENERGY_KEYS}
    for model, profile in INVERTER_PROFILES.items():
        for connection_type, connection_type_profile in profile.connection_types.items():
            for inv in connection_type_profile.versions.values():
                serialized = [f.serialize(inv, connection_type_profile.register_type) for f in ENTITIES]
                found = {s["key"] for s in serialized if s is not None and s["key"] in keys}
                assert found in ({MODBUS_PV_ENERGY_KEY}, set(INTEGRATED_PV_ENERGY_KEYS)), (model, connection_type, inv)


@pytest.mark.parametrize(
    ("base_model", "connection_type", "expected"),
    [
        ("H3", "AUX", [MODBUS_PV_ENERGY_KEY]),
        ("H1", "LAN", sorted(INTEGRATED_PV_ENERGY_KEYS)),
    ],
)
def test_energy_dashboard_solar_source(base_model: str, connection_type: str, expected: list[str]) -> None:
    flow = SimpleNamespace(_inverter_data_to_dict=lambda _: {INVERTER_BASE: base_model, INVERTER_CONN: connection_type})
    assert FlowHandler._solar_energy_keys(flow, None) == expected  # type: ignore[arg-type]  # noqa: SLF001
