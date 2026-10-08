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


def test_web_settings_are_named() -> None:
    """FoxESS web settings matched to documented registers by name and value (2026-10-08)"""
    entities = _h3_193()
    expected = {
        "inverter_power_on": ([49077], "Inverter SysOn/Off"),
        "drm_state": ([49206], "Inverter DRMState"),
        "meter2_ct2_type": ([49208], "Meter2 Meter2"),
        "standby_state": ([49229], "Inverter StandbyState"),
        "time_mode_flag": ([48000], "Inverter TimeModeFlag"),
        "time_group_1_enable": ([48010], "Inverter Time1Disable/Enable"),
        "time_group_1_start": ([48011], "Inverter StartTime1"),
        "time_group_1_end": ([48012], "Inverter EndTime1"),
        "time_group_1_work_mode": ([48013], "Inverter Time1WorkMode"),
        "legacy_inverter_power_on": ([41014], "Inverter SysOn/Off Legacy"),
        "legacy_standby_state": ([44031], "Inverter StandbyState Legacy"),
    }
    for key, (addresses, name) in expected.items():
        assert entities[key]["addresses"] == addresses, key
        assert entities[key]["name"] == name, key
    for address in (48000, 48010, 48011, 48012, 48013, 49077, 49206, 49229):
        assert f"register_{address}_raw" not in entities


def test_web_setting_codes() -> None:
    by_key = {getattr(f, "key", None): f for f in ENTITIES}
    assert by_key["standby_state"].formatter([1]) == "On"  # type: ignore[attr-defined]
    assert by_key["inverter_power_on"].formatter([0]) == "Unknown (0)"  # type: ignore[attr-defined]
    # Written 0x0A1E / 0x0B2D, the FoxESS web settings showed 10:30 / 11:45 (2026-10-08)
    assert by_key["time_group_1_start"].formatter([0x0A1E]) == "10:30"  # type: ignore[attr-defined]
    assert by_key["time_group_1_end"].formatter([0x0B2D]) == "11:45"  # type: ignore[attr-defined]
    assert by_key["time_group_1_work_mode"].formatter([1]) == "SelfUse"  # type: ignore[attr-defined]


def test_all_96_time_groups() -> None:
    entities = _h3_193()
    for n in (1, 2, 50, 96):
        start = 48010 + 10 * (n - 1)
        assert entities[f"time_group_{n}"]["addresses"] == list(range(start, start + 7)), n
        assert entities[f"time_group_{n}"]["name"] == f"Inverter Time{n}"
    assert "time_group_97" not in entities
    by_key = {getattr(f, "key", None): f for f in ENTITIES}
    # Group 1 during the 2026-10-08 write test, as the FoxESS web settings showed it
    values = [0, 0x0A1E, 0x0B2D, 1, 0x640A, 10, 1234]
    expected = "disable 10:30-11:45 SelfUse, MaxSoCFromGrid 100%, MinSoCOnGrid 10%, FC/FDSOC 10%, FC/FDPWR 1234 W"
    assert by_key["time_group_1"].formatter(values) == expected  # type: ignore[attr-defined]


def test_peak_shaving_and_balance_as_on_the_web() -> None:
    entities = _h3_193()
    assert entities["chr_in_low_import"]["name"] == "Inverter ChrInLowImport"
    assert entities["chr_in_low_start_time1_hour"]["addresses"] == [46507]
    assert entities["chr_in_low_end_time2_minute"]["addresses"] == [46514]
    assert entities["chr_in_low_end_time2_minute"]["name"] == "Inverter ChrInLowEndTime2Minute"
    assert entities["balance_logic_first"]["addresses"] == [46615]
    assert entities["legacy_balance_logic_first"]["addresses"] == [41026]
    assert entities["reg_46504_export_peak_limit"]["name"] == "Inverter Exportpeaklimit"
    by_key = {getattr(f, "key", None): f for f in ENTITIES}
    assert by_key["chr_in_low_import"].formatter([2]) == "TimingMode"  # type: ignore[attr-defined]


def test_peak_shaving_legacy_block() -> None:
    """44016-44029 mirror 46501-46514: unique values written to every field showed up at both (2026-10-08)"""
    entities = _h3_193()
    assert entities["legacy_import_power_limit"]["addresses"] == [44017, 44016]
    assert entities["legacy_reg_46503_threshold_soc"]["addresses"] == [44018]
    assert entities["legacy_reg_46504_export_peak_limit"]["addresses"] == [44020, 44019]
    assert entities["legacy_chr_in_low_import"]["addresses"] == [44021]
    assert entities["legacy_chr_in_low_start_time1_hour"]["addresses"] == [44022]
    assert entities["legacy_chr_in_low_end_time2_minute"]["addresses"] == [44029]
    assert entities["legacy_chr_in_low_import"]["name"] == "Inverter ChrInLowImport Legacy"
    assert entities["import_power_limit"]["name"] == "Inverter Importlimit"
