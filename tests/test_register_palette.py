"""Playground register palette: the legacy and the documented-map register of an entity are both visible."""

from types import SimpleNamespace
from typing import Any

import pytest

from custom_components.foxess_modbus.common.types import Inv
from custom_components.foxess_modbus.common.types import RegisterType
from custom_components.foxess_modbus.const import DOMAIN
from custom_components.foxess_modbus.const import FRIENDLY_NAME
from custom_components.foxess_modbus.const import INVERTER_CONN
from custom_components.foxess_modbus.const import INVERTER_MODEL
from custom_components.foxess_modbus.entities.discovered_registers import _fix_missing_sign_extension
from custom_components.foxess_modbus.entities.entity_descriptions import ENTITIES
from custom_components.foxess_modbus.entities.entity_grouping import is_palette
from custom_components.foxess_modbus.entities.modbus_entity_mixin import ModbusEntityMixin


def _h3_193() -> dict[str, Any]:
    result = {}
    for factory in ENTITIES:
        serialized = factory.serialize(Inv.H3_193, RegisterType.HOLDING)
        if serialized is not None and serialized["type"] == "sensor":
            result[serialized["key"]] = serialized
    return result


def test_battery_current_keeps_the_documented_register_next_to_the_legacy_one() -> None:
    entities = _h3_193()
    assert entities["bat_current"]["addresses"] == [39229, 39228]  # unknown while charging; the user picks
    assert entities["legacy_bat_current"]["addresses"] == [31035]
    assert entities["bat_current_1"]["addresses"] == [37610]  # the BMS' own measurement


def test_pv_power_follows_39118() -> None:
    entities = _h3_193()
    # Legacy PV1 power equals 39118 and the FoxESS Cloud; the documented 39279 is DC voltage x current
    assert entities["pv1_power"]["addresses"] == [31002]
    assert entities["pv2_power"]["addresses"] == [31005]
    assert entities["newmap_pv1_power"]["addresses"] == [39280, 39279]
    assert entities["pv_power_now"]["addresses"] == [39119, 39118]


def test_every_twin_mirrors_an_entity() -> None:
    entities = _h3_193()
    twins = [key for key in entities if is_palette(key)]
    assert len(twins) > 50
    for key in twins:
        assert key.removeprefix("legacy_").removeprefix("newmap_") in entities, key
        assert entities[key]["name"].endswith((" Legacy", " New Map")), key


@pytest.mark.parametrize(("raw", "expected"), [(65.506, -0.030), (32.768, -32.768), (1.234, 1.234), (-0.5, -0.5)])
def test_missing_sign_extension(raw: float, expected: float) -> None:
    assert _fix_missing_sign_extension(raw) == pytest.approx(expected)


def test_palette_device() -> None:
    entity = SimpleNamespace(
        entity_description=SimpleNamespace(key="legacy_bat_current"),
        _controller=SimpleNamespace(
            inverter_details={FRIENDLY_NAME: "inv", INVERTER_MODEL: "H3", INVERTER_CONN: "AUX"}
        ),
    )
    info: dict[str, Any] = ModbusEntityMixin.device_info.fget(entity)  # type: ignore[attr-defined]
    assert info["identifiers"] == {(DOMAIN, "H3", "AUX", "inv", "palette")}
    assert info["via_device"] == (DOMAIN, "H3", "AUX", "inv")
    assert info["name"] == "FoxESS - Modbus (inv) Register Palette"
