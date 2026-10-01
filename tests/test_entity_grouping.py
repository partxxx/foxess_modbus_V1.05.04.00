"""Sensors, diagnostics and the experimental device; keys and unique ids don't change."""

from types import SimpleNamespace
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
from custom_components.foxess_modbus.const import INVERTER_CONN
from custom_components.foxess_modbus.const import INVERTER_MODEL
from custom_components.foxess_modbus.entities.entity_descriptions import ENTITIES
from custom_components.foxess_modbus.entities.entity_grouping import DIAGNOSTIC_KEYS
from custom_components.foxess_modbus.entities.entity_grouping import EXPERIMENTAL_KEYS
from custom_components.foxess_modbus.entities.entity_grouping import is_diagnostic
from custom_components.foxess_modbus.entities.entity_grouping import is_experimental
from custom_components.foxess_modbus.entities.modbus_entity_mixin import ModbusEntityMixin
from custom_components.foxess_modbus.services import utils


def _h3_193() -> list:
    return [f for f in ENTITIES if f.serialize(Inv.H3_193, RegisterType.HOLDING) is not None]


def test_grouped_keys_exist() -> None:
    keys = {f.key for f in ENTITIES}
    # connection_status is created by the platform; state_code is replaced by inverter_state on H3_193
    assert DIAGNOSTIC_KEYS - keys == {"connection_status"}
    assert EXPERIMENTAL_KEYS <= {f.key for f in _h3_193()}
    assert not DIAGNOSTIC_KEYS & EXPERIMENTAL_KEYS


def test_categories() -> None:
    for factory in _h3_193():
        key = factory.key
        if not isinstance(factory, SensorEntityDescription):
            assert factory.entity_category is None, key  # numbers and selects stay controls
        elif is_diagnostic(factory):
            assert factory.entity_category == EntityCategory.DIAGNOSTIC, key
        elif key.startswith(("reg_", "register_")):
            assert factory.entity_category is None, key
        if isinstance(factory, SensorEntityDescription) and (key in DIAGNOSTIC_KEYS or key.startswith(("reg_", "register_"))):
            assert factory.entity_registry_enabled_default, key


def test_experimental_selection() -> None:
    raw = {f.key for f in _h3_193() if f.key.startswith("register_")}
    assert raw and all(is_experimental(key) for key in raw)
    assert not is_experimental("reg_37615_bms_max_current_candidate")  # proven: the API's maxChargeCurrent
    assert not is_experimental("reg_38832_grid_ct1_r_phase_apparent")  # proven: S = U * I
    assert is_experimental("reg_39142_ambtemp_candidate")


def test_only_measured_quantities_are_sensors() -> None:
    by_key = {f.key: f for f in _h3_193() if isinstance(f, SensorEntityDescription)}
    for key in ("battery_soc", "battery_soh", "batvolt", "pv1_current", "load_power", "solar_energy_total", "invtemp",
                "inverter_date_time"):
        assert by_key[key].entity_category is None, key
    for key in ("master_version", "inverter_state", "inverter_fault_code", "max_soc", "grid_standard",
                "meter1_ct1_type", "bms_max_current", "reg_39053_rated_power_pn", "reg_39067_alarm_1"):
        assert by_key[key].entity_category == EntityCategory.DIAGNOSTIC, key
    assert by_key["inverter_date_time"].entity_registry_enabled_default


def _device(key: str) -> dict:
    entity = SimpleNamespace(
        entity_description=SimpleNamespace(key=key),
        _controller=SimpleNamespace(inverter_details={FRIENDLY_NAME: "inv", INVERTER_MODEL: "H3", INVERTER_CONN: "AUX"}),
    )
    return ModbusEntityMixin.device_info.fget(entity)  # type: ignore[attr-defined]


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
    monkeypatch.setattr(device_registry, "async_get", lambda _hass: SimpleNamespace(async_get=Mock(return_value=device)))
    assert utils.get_controller_from_friendly_name_or_device_id("id", [controller], MagicMock()) is controller
