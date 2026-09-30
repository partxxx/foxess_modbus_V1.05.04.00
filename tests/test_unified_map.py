"""Offline coverage for the opt-in unified map; no real Modbus connections."""

from collections import defaultdict
from typing import Any
from unittest.mock import MagicMock

import pytest
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

from custom_components.foxess_modbus.common.types import Inv
from custom_components.foxess_modbus.common.types import RegisterType
from custom_components.foxess_modbus.const import ENTITY_ID_PREFIX
from custom_components.foxess_modbus.const import EXPERIMENTAL_UNIFIED_MAP
from custom_components.foxess_modbus.const import INVERTER_BASE
from custom_components.foxess_modbus.const import INVERTER_CONN
from custom_components.foxess_modbus.const import RAW_REGISTER_ENTITIES
from custom_components.foxess_modbus.const import UNIQUE_ID_PREFIX
from custom_components.foxess_modbus.entities.entity_descriptions import ENTITIES
from custom_components.foxess_modbus.inverter_profiles import INVERTER_PROFILES


@pytest.mark.parametrize("inv,expected_count", [(Inv.UNIFIED_1PH, 201), (Inv.UNIFIED_3PH, 235)])
def test_unified_entities(inv: Inv, expected_count: int, snapshot: SnapshotAssertion) -> None:
    entities: list[dict[str, Any]] = []
    for factory in ENTITIES:
        serialized = factory.serialize(inv, RegisterType.HOLDING)
        if serialized is not None:
            assert factory.entity_type is SensorEntity
            entities.append(serialized)
    entities.sort(key=lambda item: item["key"])
    keys = [item["key"] for item in entities]
    assert len(keys) == len(set(keys)) == expected_count
    assert {"pv3_voltage", "pv3_current", "pv3_power", "pv3_energy_total"} <= set(keys)
    assert "ambtemp" not in keys
    assert "bms_max_current" not in keys
    assert all(
        address >= 36000 and not 40000 <= address <= 44999 for item in entities for address in item.get("addresses", [])
    )
    assert entities == snapshot.use_extension(extension_class=JSONSnapshotExtension)


async def test_unified_profiles_are_read_only(hass: HomeAssistant) -> None:
    offered = 0
    for profile in INVERTER_PROFILES.values():
        for connection_type, connection_profile in profile.connection_types.items():
            if connection_profile.unified_inv is None:
                continue
            offered += 1
            controller = MagicMock()
            controller.hass = hass
            controller.inverter_details = {
                INVERTER_BASE: profile.model,
                INVERTER_CONN: connection_type,
                ENTITY_ID_PREFIX: "",
                UNIQUE_ID_PREFIX: "",
                RAW_REGISTER_ENTITIES: True,
                EXPERIMENTAL_UNIFIED_MAP: True,
            }
            assert connection_profile.create_remote_control_config(controller) is None
            assert connection_profile.create_charge_periods(controller) == []
            for entity_type in (NumberEntity, SelectEntity, BinarySensorEntity):
                assert connection_profile.create_entities(entity_type, controller) == []
            sensors = connection_profile.create_entities(
                SensorEntity, controller, filter_depends_on_other_entites=False
            )
            assert len(sensors) > 100
            assert len({sensor.entity_id for sensor in sensors}) == len(sensors)
            for sensor in sensors:
                for address in getattr(sensor, "addresses", []):
                    assert address >= 36000 and not 40000 <= address <= 44999
                    assert not connection_profile.overlaps_invalid_range(address, address, controller)
    assert offered == 13


# Sensors which read the same registers on purpose: one signed value split by direction, and the two bytes of 48014
_SHARED_REGISTER_GROUPS = [
    {"grid_ct", "feed_in", "grid_consumption"},
    *({f"grid_ct_{phase}", f"feed_in_{phase}", f"grid_consumption_{phase}"} for phase in "RST"),
    {"invbatpower", "battery_charge", "battery_discharge"},
    {"invbatpower_1", "battery_charge_1", "battery_discharge_1"},
    {"time_group_1_max_soc_from_grid", "time_group_1_min_soc_on_grid"},
]


@pytest.mark.parametrize("inv", [Inv.H3_193, Inv.UNIFIED_1PH, Inv.UNIFIED_3PH])
def test_no_duplicate_register_sensors(inv: Inv) -> None:
    keys_by_addresses: dict[tuple[int, ...], set[str]] = defaultdict(set)
    for factory in ENTITIES:
        serialized = factory.serialize(inv, RegisterType.HOLDING)
        if serialized is not None and serialized["type"] == "sensor":
            keys_by_addresses[tuple(sorted(serialized["addresses"]))].add(serialized["key"])
    for keys in keys_by_addresses.values():
        if len(keys) > 1:
            assert any(keys <= group for group in _SHARED_REGISTER_GROUPS), keys


@pytest.mark.parametrize("inv", [Inv.H3_193, Inv.UNIFIED_1PH, Inv.UNIFIED_3PH])
def test_pv_power_is_read_from_the_inverter(inv: Inv) -> None:
    serialized = [factory.serialize(inv, RegisterType.HOLDING) for factory in ENTITIES]
    assert [item for item in serialized if item is not None and item["key"] == "pv_power_now"] == [
        {
            "type": "sensor",
            "key": "pv_power_now",
            "name": "PV Power",
            "addresses": [39119, 39118],
            "scale": 0.001,
            "signed": True,
        }
    ]
