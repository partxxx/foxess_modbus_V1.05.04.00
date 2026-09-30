"""Display-name regression tests, including source and identifier preservation."""

# Reconstruct the unmodified descriptions to prove that naming does not change behavior.
# ruff: noqa: SLF001

import itertools
import re
from dataclasses import fields
from typing import Any
from typing import cast

import pytest
from homeassistant.helpers.entity import EntityDescription

from custom_components.foxess_modbus.common.types import Inv
from custom_components.foxess_modbus.common.types import RegisterType
from custom_components.foxess_modbus.entities import discovered_registers
from custom_components.foxess_modbus.entities import entity_descriptions
from custom_components.foxess_modbus.entities.charge_period_descriptions import CHARGE_PERIODS
from custom_components.foxess_modbus.entities.entity_nomenclature import apply_entity_nomenclature
from custom_components.foxess_modbus.entities.entity_nomenclature import entity_display_name
from custom_components.foxess_modbus.entities.inverter_model_spec import ModbusAddressesSpec
from custom_components.foxess_modbus.entities.modbus_sensor import ModbusSensorDescription
from custom_components.foxess_modbus.entities.remote_control_description import REMOTE_CONTROL_DESCRIPTION


@pytest.mark.parametrize(
    ("key", "old_name", "address", "expected"),
    [
        ("batvolt", "Battery Voltage", 37609, "BMS1 BAT Voltage"),
        ("batvolt_2", "Battery 2 Voltage", 38307, "BMS2 BAT Voltage"),
        ("batvolt", "Battery Voltage", 39227, "Inverter BAT1 Voltage"),
        ("invbatvolt_2", "Inverter Battery 2 Voltage", 39232, "Inverter BAT2 Voltage"),
        ("invbatpower_1", "Inverter Battery 1 Power", 39230, "Inverter BAT1 Power"),
        ("invbatpower_2", "Inverter Battery 2 Power", 39235, "Inverter BAT2 Power"),
        ("invbatpower", "Inverter Battery Power", 39237, "Inverter BAT Power"),
        ("battery_charge", "Battery Charge", 39237, "Inverter BAT Power Charge"),
        ("battery_discharge_total", "Battery Discharge Total", 39609, "Inverter BAT Energy Discharge Total"),
        ("battery_soh", "Battery SoH", 39423, "System SoC"),
        ("battery_soc", "Battery SoC", 37612, "BMS1 BAT SoC"),
        ("bms_cell_temp_low_2", "BMS 2 Cell Temp Low", 38316, "BMS2 BAT Cell Temperature Min"),
        ("batvolt", "Battery Voltage", 11034, "BAT Voltage Source Unconfirmed"),
        ("pv1_energy_total", "PV1 Power Total", None, "PV1 Energy Total"),
        ("reg_39118_total_pv_input_power", "Total PV Input Power (39118)", 39118, "PV Power"),
        ("reg_39329_mppt1_power", "MPPT1 Power (39329)", 39329, "MPPT1 Power"),
        ("eps_rvolt_R", "EPS Voltage_R", 39201, "EPS R Voltage"),
        ("rpower_S_T", "Inverter Power (Apparent) T", 39268, "Inverter T Apparent Power"),
        ("feed_in_S", "Feed-in S", 38818, "Grid S Power Export"),
        ("grid_ct_pf_R", "Grid CT Power Factor R", 38840, "Meter CT1 R Power Factor"),
        ("eps_frequency_select", "EPS Frequency (46612)", 46612, "EPS Frequency Setting"),
        ("reg_46018_pwr_limit_bat_up", "Pwr_limit Bat_Up (46018)", 46018, "Inverter BAT Power Discharge Available"),
        ("reg_46020_pwr_limit_bat_dn", "Pwr_limit Bat_Dn (46020)", 46020, "Inverter BAT Power Charge Available"),
        ("time_period_1_start", "Period 1 - Start", None, "Time Period1 Start"),
        ("register_39134_raw", "Register 39134 raw", 39134, "Register 39134 Raw"),
    ],
)
def test_display_name(key: str, old_name: str, address: int | None, expected: str) -> None:
    assert entity_display_name(key, old_name, address) == expected
    assert entity_display_name(key, expected, address) == expected


def test_same_key_can_have_different_measurement_sources() -> None:
    original = ModbusSensorDescription(
        key="batvolt",
        name="Battery Voltage",
        addresses=[
            ModbusAddressesSpec(holding=[37609], models=Inv.H1_G2_144),
            ModbusAddressesSpec(holding=[39227], models=Inv.H3_193),
        ],
        native_unit_of_measurement="V",
        scale=0.1,
    )
    renamed = apply_entity_nomenclature([original])
    assert len(renamed) == 2
    assert {cast(EntityDescription, factory).key for factory in renamed} == {"batvolt"}
    assert {cast(EntityDescription, factory).name for factory in renamed} == {
        "BMS1 BAT Voltage",
        "Inverter BAT1 Voltage",
    }
    for inv in (Inv.H1_G2_144, Inv.H3_193):
        serialized = [factory.serialize(inv, RegisterType.HOLDING) for factory in renamed]
        supported = [value for value in serialized if value is not None]
        assert len(supported) == 1
        before = original.serialize(inv, RegisterType.HOLDING)
        assert before is not None
        assert {k: v for k, v in before.items() if k != "name"} == {
            k: v for k, v in supported[0].items() if k != "name"
        }


def test_all_profiles_preserve_every_non_name_field(monkeypatch: pytest.MonkeyPatch) -> None:
    # Rebuild the real pre-naming descriptions, including H3 ports and unified-map clones.
    monkeypatch.setattr(discovered_registers, "apply_entity_nomenclature", list)
    originals = discovered_registers.apply_discovered_registers(
        itertools.chain(
            entity_descriptions._version_entities(),
            entity_descriptions._pv_entities(),
            entity_descriptions._h1_current_voltage_power_entities(),
            entity_descriptions._h3_current_voltage_power_entities(),
            entity_descriptions._inverter_entities(),
            entity_descriptions._bms_entities(),
            entity_descriptions._configuration_entities(),
            (description for period in CHARGE_PERIODS for description in period.entity_descriptions),
            REMOTE_CONTROL_DESCRIPTION.entity_descriptions,
        )
    )
    for original in originals:
        key = cast(EntityDescription, original).key
        renamed = apply_entity_nomenclature([original])
        for factory in renamed:
            for field in fields(cast(Any, original)):
                if field.name not in ("name", "address", "addresses"):
                    assert getattr(original, field.name) == getattr(factory, field.name), (key, field.name)
        for inv in Inv:
            for register_type in RegisterType:
                before = original.serialize(inv, register_type)
                serialized = [factory.serialize(inv, register_type) for factory in renamed]
                after = [value for value in serialized if value is not None]
                if before is None:
                    assert not after, (key, inv, register_type)
                else:
                    assert len(after) == 1, (key, inv, register_type)
                    assert {k: v for k, v in before.items() if k != "name"} == {
                        k: v for k, v in after[0].items() if k != "name"
                    }


def test_names_follow_nomenclature() -> None:
    for factory in entity_descriptions.ENTITIES:
        description = cast(EntityDescription, factory)
        name = description.name
        assert isinstance(name, str)
        assert "_" not in name
        assert not re.search(r"\b(?:Temp|Minimum|Maximum|Lifetime)\b", name), name
        assert not re.search(r"\b(?:PV|BAT|BMS|CT|MPPT) \d", name), name
        assert not re.search(r" \([0-9]{5}\)$", name), name
        assert not re.search(r"^(?:Inverter|Grid|EPS|Load|Meter CT[12]) .+ [RST]$", name), name
        if getattr(factory, "native_unit_of_measurement", None) in ("Wh", "kWh"):
            assert "Energy" in name, (description.key, name)
