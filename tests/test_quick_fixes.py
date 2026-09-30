"""Regression tests for model detection, dependent sensors and device lookup."""

import re
from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry
from homeassistant.helpers import entity_registry

from custom_components.foxess_modbus.common.types import ConnectionType
from custom_components.foxess_modbus.common.types import InverterModel
from custom_components.foxess_modbus.const import DOMAIN
from custom_components.foxess_modbus.const import ENTITY_ID_PREFIX
from custom_components.foxess_modbus.const import FRIENDLY_NAME
from custom_components.foxess_modbus.const import INVERTER_BASE
from custom_components.foxess_modbus.const import INVERTER_CONN
from custom_components.foxess_modbus.const import UNIQUE_ID_PREFIX
from custom_components.foxess_modbus.entities.modbus_lambda_sensor import ModbusLambdaSensor
from custom_components.foxess_modbus.entities.modbus_lambda_sensor import ModbusLambdaSensorDescription
from custom_components.foxess_modbus.inverter_profiles import INVERTER_PROFILES
from custom_components.foxess_modbus.services import utils


@pytest.mark.parametrize(
    "model_name,expected,capacity",
    [
        ("H3-12.0-SMART", InverterModel.H3_SMART, 12000),
        ("H3-8.0-Smart", InverterModel.H3_SMART, 8000),
        ("H3-15.0-smart", InverterModel.H3_SMART, 15000),
        ("H3-10.0-sMaRt", InverterModel.H3_SMART, 10000),
        ("H3-12.0-M", InverterModel.H3_SMART, 12000),
        ("H3-5.0-E", InverterModel.H3, 5000),
        ("H3-Pro-20.0", InverterModel.H3_PRO, 20000),
        ("P3-10.0-SH1", InverterModel.P3_SMART, 10000),
    ],
)
def test_model_detection_order(model_name: str, expected: InverterModel, capacity: int) -> None:
    profile = next(profile for profile in INVERTER_PROFILES.values() if re.match(profile.model_pattern, model_name))
    assert profile.model == expected
    assert profile.inverter_capacity(model_name) == capacity


async def test_lambda_created_after_source_registration(hass: HomeAssistant) -> None:
    controller = MagicMock()
    controller.hass = hass
    controller.inverter_details = {
        INVERTER_BASE: InverterModel.H3_SMART,
        INVERTER_CONN: ConnectionType.AUX,
        ENTITY_ID_PREFIX: "test",
        UNIQUE_ID_PREFIX: "test",
    }
    profile = INVERTER_PROFILES[InverterModel.H3_SMART].connection_types[ConnectionType.AUX]
    independent = profile.create_entities(SensorEntity, controller, filter_depends_on_other_entites=False)
    assert not any(isinstance(sensor, ModbusLambdaSensor) for sensor in independent)
    assert {"pv1_power", "pv2_power"} <= {sensor.entity_description.key for sensor in independent}

    registry = entity_registry.async_get(hass)
    source = registry.async_get_or_create(
        "sensor", DOMAIN, "foxess_modbus_test_pv1_power", suggested_object_id="renamed_pv1"
    )
    for index in range(2, 5):
        registry.async_get_or_create(
            "sensor", DOMAIN, f"foxess_modbus_test_pv{index}_power", suggested_object_id=f"test_pv{index}_power"
        )
    dependent = profile.create_entities(SensorEntity, controller, filter_depends_on_other_entites=True)
    sensor = next(sensor for sensor in dependent if isinstance(sensor, ModbusLambdaSensor))
    assert isinstance(sensor, ModbusLambdaSensor)
    assert isinstance(sensor.entity_description, ModbusLambdaSensorDescription)
    assert sensor.entity_description.depends_on_other_entities
    assert source.entity_id in sensor._source_entity_ids  # noqa: SLF001


@pytest.mark.parametrize("device_id", ["device-id", "inverter"])
def test_controller_lookup_uses_registry_api(monkeypatch: pytest.MonkeyPatch, device_id: str) -> None:
    controller = MagicMock()
    controller.inverter_details = {FRIENDLY_NAME: "inverter"}
    device = SimpleNamespace(identifiers={(DOMAIN, "model", "aux", "inverter")})
    lookup = Mock(return_value=device if device_id == "device-id" else None)
    # Deliberately no .devices mapping: accessing the deprecated API must fail.
    registry = SimpleNamespace(async_get=lookup)
    monkeypatch.setattr(device_registry, "async_get", lambda _hass: registry)
    assert utils.get_controller_from_friendly_name_or_device_id(device_id, [controller], MagicMock()) is controller
    lookup.assert_called_once_with(device_id)


def test_controller_lookup_rejects_foreign_device(monkeypatch: pytest.MonkeyPatch) -> None:
    device = SimpleNamespace(identifiers={("other_integration", "model", "aux", "inverter")})
    registry = SimpleNamespace(async_get=Mock(return_value=device))
    monkeypatch.setattr(device_registry, "async_get", lambda _hass: registry)
    with pytest.raises(HomeAssistantError, match="not an inverter"):
        utils.get_controller_from_friendly_name_or_device_id("device-id", [MagicMock()], MagicMock())


@pytest.mark.parametrize("device_id", ["missing", None])
def test_controller_lookup_unknown_name(monkeypatch: pytest.MonkeyPatch, device_id: str | None) -> None:
    controller = MagicMock()
    controller.inverter_details = {FRIENDLY_NAME: "inverter"}
    registry = SimpleNamespace(async_get=Mock(return_value=None))
    monkeypatch.setattr(device_registry, "async_get", lambda _hass: registry)
    with pytest.raises(HomeAssistantError, match="Unable to find an inverter"):
        utils.get_controller_from_friendly_name_or_device_id(device_id, [controller], MagicMock())


def test_controller_lookup_no_inverters() -> None:
    with pytest.raises(HomeAssistantError, match="No inverters configured"):
        utils.get_controller_from_friendly_name_or_device_id("device-id", [], MagicMock())
