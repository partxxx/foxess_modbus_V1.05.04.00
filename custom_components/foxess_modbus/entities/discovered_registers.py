"""
Registers of FoxESS H3 on Manager 1.93+ (Inv.H3_193), read from the "new" register map
(FoxESS Modbus definition V1.05.04.00, 2025-12-15), measured on an H3-5.0-E on 2026-09-30.

- _SWAPS: existing entities verified against the legacy map or an independent consistency check (load phase
  sum; grid values against a HomeWizard P1 meter). On H3_193 these entities read the new register instead.
- _REMOVE: entities dropped on H3_193 (pv_power_now; state_code, replaced by the decoded inverter_state).
- _VERSIONS: the Master / Slave / Manager versions from 36001-36003 (the legacy 30016-30018 hold serial number
  characters on this firmware).
- _WRITABLE_PORTS / _SELECT_PORTS: the writable settings (charge/discharge current, SoC limits, export limit,
  work mode, balance mode) moved to their new-map registers, both the controls and their read-only sensors.
- _FROM_H3_SMART: entities the integration already defines for H3-Smart (same new map), whose registers answer
  with plausible values on H3_193. Added for H3_193, disabled by default.
- _DECODED: documented codes, versions and date/time decoded to text, disabled by default.
- _NAMED: further documented registers with a known meaning and unit, as read-only sensors, disabled by default.
- _DEVELOPER: new-map counterparts of the entities kept on their legacy register (ambient temperature, BMS max
  current, fault words), for comparing the two over time.
- _RAW: registers whose value can't be interpreted yet (status words, codes, registers with a known encoding bug),
  as "Register xxxxx raw".
  _DEVELOPER and _RAW are only created when the "raw register entities" advanced option is on, and disabled by
  default.

_add_unified_map then adds the EXPERIMENTAL unified map (Inv.UNIFIED_SET): the read-only H3_193 entities which
only use the new map, plus the fault code and PV3 from the H3-Smart definitions.

Not included: registers answering IllegalAddress on this firmware (added to the invalid ranges instead),
reserved and write-only registers, strings, and hardware this inverter doesn't have (PV3+ on H3_193, MPPT3, BMS2,
Meter2/CT2).

The tables originated from the measured register list and include subsequent live-test corrections.
"""

import copy
from dataclasses import dataclass
from dataclasses import replace
from typing import Any
from typing import Callable
from typing import Iterable
from typing import TypeVar
from typing import cast

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity import EntityDescription

from ..common.entity_controller import EntityController
from ..common.types import Inv
from ..common.types import RegisterPollType
from ..common.types import RegisterType
from ..const import RAW_REGISTER_ENTITIES
from ..const import ROUND_SENSOR_VALUES
from .entity_factory import ENTITY_DESCRIPTION_KWARGS
from .entity_factory import EntityFactory
from .entity_nomenclature import apply_entity_nomenclature
from .inverter_model_spec import EntitySpec
from .inverter_model_spec import InverterModelSpec
from .inverter_model_spec import ModbusAddressesSpec
from .inverter_model_spec import ModbusAddressSpec
from .inverter_model_spec import ModbusAddressSpecBase
from .modbus_battery_sensor import ModbusBatterySensorDescription
from .modbus_integration_sensor import ModbusIntegrationSensorDescription
from .modbus_inverter_state_sensor import ModbusG2InverterStateSensorDescription
from .modbus_sensor import ModbusSensor
from .modbus_sensor import ModbusSensorDescription
from .modbus_version_sensor import ModbusVersionSensorDescription

# key -> (addresses, low-order word first; scale; signed as in the V1.05.04.00 register type)
_SWAPS: dict[str, tuple[list[int], float | None, bool]] = {
    "battery_charge": ([39238, 39237], 0.001, True),
    "battery_charge_total": ([39606, 39605], 0.01, False),
    "battery_discharge": ([39238, 39237], 0.001, True),
    "battery_discharge_total": ([39610, 39609], 0.01, False),
    "battery_soc": ([37612], None, False),
    # Legacy 31xxx pairs matched live 2026-09-30 15:52 (two independent reads, battery current at 6 A). Inverter side
    # battery voltage/current, not the BMS' own 37609/37610.
    "eps_frequency": ([39218], 0.01, True),
    "batvolt": ([39227], 0.1, True),
    "bat_current": ([39229, 39228], 0.001, True),
    "battery_temp": ([37611], 0.1, True),
    "battery_soh": ([37624], None, False),
    "bms_cell_temp_high": ([37617], 0.1, True),
    "bms_cell_temp_low": ([37618], 0.1, True),
    "bms_kwh_remaining": ([37632], 0.01, False),
    "bms_cell_mv_high": ([37619], None, False),
    "bms_cell_mv_low": ([37620], None, False),
    "eps_power_R": ([39211, 39210], 0.001, True),
    "eps_power_S": ([39213, 39212], 0.001, True),
    "eps_power_T": ([39215, 39214], 0.001, True),
    "feed_in_R": ([38817, 38816], 0.0001, True),
    "feed_in_S": ([38819, 38818], 0.0001, True),
    "feed_in_T": ([38821, 38820], 0.0001, True),
    "feed_in_energy_today": ([39616, 39615], 0.01, False),
    "feed_in_energy_total": ([39614, 39613], 0.01, False),
    "grid_consumption_R": ([38817, 38816], 0.0001, True),
    "grid_consumption_S": ([38819, 38818], 0.0001, True),
    "grid_consumption_T": ([38821, 38820], 0.0001, True),
    "grid_consumption_energy_today": ([39620, 39619], 0.01, False),
    "grid_consumption_energy_total": ([39618, 39617], 0.01, False),
    "grid_ct_R": ([38817, 38816], 0.0001, True),
    "grid_ct_S": ([38819, 38818], 0.0001, True),
    "grid_ct_T": ([38821, 38820], 0.0001, True),
    "grid_voltage_R": ([39123], 0.1, True),
    "grid_voltage_S": ([39124], 0.1, True),
    "grid_voltage_T": ([39125], 0.1, True),
    "input_energy_today": ([39628, 39627], 0.01, False),
    "input_energy_total": ([39626, 39625], 0.01, False),
    "inv_current_R": ([39127, 39126], 0.001, True),
    "inv_current_S": ([39129, 39128], 0.001, True),
    "inv_current_T": ([39131, 39130], 0.001, True),
    "inv_power_R": ([39249, 39248], 0.001, True),
    "inv_power_S": ([39251, 39250], 0.001, True),
    "inv_power_T": ([39253, 39252], 0.001, True),
    "invbatpower": ([39238, 39237], 0.001, True),
    "invtemp": ([39141], 0.1, True),
    "load_energy_today": ([39632, 39631], 0.01, False),
    "load_power": ([39226, 39225], 0.001, True),
    "load_power_R": ([39220, 39219], 0.001, True),
    "load_power_S": ([39222, 39221], 0.001, True),
    "load_power_T": ([39224, 39223], 0.001, True),
    "load_power_total": ([39630, 39629], 0.01, False),
    "pv1_current": ([39071], 0.01, True),
    "pv1_power": ([39280, 39279], 0.001, True),
    "pv1_voltage": ([39070], 0.1, True),
    "pv2_current": ([39073], 0.01, True),
    "pv2_power": ([39282, 39281], 0.001, True),
    "pv2_voltage": ([39072], 0.1, True),
    "rfreq": ([39139], 0.01, True),
    "solar_energy_today": ([39604, 39603], 0.01, False),
    "solar_energy_total": ([39602, 39601], 0.01, False),
    "total_yield_today": ([39624, 39623], 0.01, False),
    "total_yield_total": ([39622, 39621], 0.01, False),
}

# Entities which don't apply to H3_193: computed (pv_power_now = PV1 + PV2, see 39118 instead)
# state_code (31041, a bare number) is replaced by the decoded inverter_state below
_REMOVE = {"pv_power_now", "state_code"}

# The legacy version registers (30016-30018) hold serial number characters on this firmware.
# key -> (address, is_hex). Decoding confirmed against the FoxESS cloud: Master and Slave are decimal (e.g. raw 103
# = 1.03), Manager / ARM is a hex byte pair (raw 405 = 0x0195 = 1.95).
_VERSIONS: dict[str, tuple[int, bool]] = {
    "master_version": (36001, False),
    "slave_version": (36002, False),
    "manager_version": (36003, True),
}

# Writable settings moved to the new map (numbers and their read-only sensors). On 2026-09-30 each read back
# identical at the legacy and the new address, and writing the unchanged value to the new address was accepted.
# key -> addresses (low-order word first)
_WRITABLE_PORTS: dict[str, list[int]] = {
    "max_charge_current": [46607],
    "max_discharge_current": [46608],
    "min_soc": [46609],
    "max_soc": [46610],
    "min_soc_on_grid": [46611],
    "export_power_limit": [46617, 46616],
}
# Sensor signedness per the V1.05.04.00 register type, where it differs from the legacy entity
_WRITABLE_PORT_SIGNED = {"min_soc": False, "max_soc": False, "min_soc_on_grid": False}

# key -> (address, options map, or None to keep the legacy one). Balance mode: both 41025 and 46614 reject 2
# (Per Phase) on write, which can only be set on the inverter panel; reading shows it at both addresses.
_SELECT_PORTS: dict[str, tuple[int, dict[int, str] | None]] = {
    "work_mode": (
        49203,
        {1: "Self Use", 2: "Feed-in First", 3: "Back-up", 4: "Peak Shaving"},
    ),
    "balance_mode": (46614, None),
}

# Grid CT power factor: H3-Pro entities with the scale documented for H3 (raw / 1000, which matches |P| / S)
_POWER_FACTOR: dict[str, list[int]] = {
    "grid_ct_pf": [38839, 38838],
    "grid_ct_pf_R": [38841, 38840],
    "grid_ct_pf_S": [38843, 38842],
    "grid_ct_pf_T": [38845, 38844],
}
_POWER_FACTOR_SCALE = 0.001

# Inverter state from the new-map status words, decoded like the H3-Smart: Status 1, then both words of Status 3.
# Live 2026-09-30: Status 1 = 0x0004 (Operation) while legacy 31041 = 2 (On Grid)
_INVERTER_STATE_ADDRESSES = [39063, 39065, 39066]

# Templates whose H3-Smart signedness differs from the V1.05.04.00 register type
_TEMPLATE_SIGNED = {
    "batvolt_1": False,
    "battery_charge_today": False,
    "battery_discharge_today": False,
}

_FROM_H3_SMART = [
    "bat_current_1",
    "battery_soh_1",
    "battery_temp_1",
    "batvolt_1",
    "bms_cell_mv_high_1",
    "bms_cell_mv_low_1",
    "bms_cell_temp_high_1",
    "bms_cell_temp_low_1",
    "bms_kwh_remaining_1",
    "eps_rcurrent_R",
    "eps_rcurrent_S",
    "eps_rcurrent_T",
    "eps_rvolt_R",
    "eps_rvolt_S",
    "eps_rvolt_T",
    "grid_ct",
    "feed_in",
    "grid_consumption",
    "invbatcurrent_1",
    "invbatvolt_1",
    "invbatpower_1",
    "battery_charge_1",
    "battery_discharge_1",
    "rpower_S_R",
    "rpower_S_S",
    "rpower_S_T",
    "import_power_limit",
    "battery_charge_today",
    "battery_discharge_today",
]


class _PollOnceSensor(ModbusSensor):
    """A sensor whose value doesn't change, read once per connection"""

    @property
    def register_poll_type(self) -> RegisterPollType:
        return RegisterPollType.ON_CONNECTION


@dataclass(kw_only=True, **ENTITY_DESCRIPTION_KWARGS)
class DiscoveredRegisterSensorDescription(ModbusSensorDescription):  # type: ignore[misc]
    """ModbusSensorDescription which can be read once per connection, or be a raw register"""

    poll_once: bool = False
    raw: bool = False

    def create_entity_if_supported(
        self,
        controller: EntityController,
        inverter_model: Inv,
        register_type: RegisterType,
    ) -> Entity | None:
        if self.raw and not controller.inverter_details.get(RAW_REGISTER_ENTITIES, False):
            return None
        addresses = self._addresses_for_inverter_model(self.addresses, inverter_model, register_type)
        if addresses is None:
            return None
        round_to = self.round_to if controller.inverter_details.get(ROUND_SENSOR_VALUES, False) else None
        sensor_type = _PollOnceSensor if self.poll_once else ModbusSensor
        return sensor_type(controller, self, addresses, round_to)


class _TextSensor(ModbusSensor):
    """A sensor whose value is text decoded from one or more registers"""

    def _calculate_native_value(self) -> Any:
        description = cast(DiscoveredTextSensorDescription, self.entity_description)
        values = [self._controller.read(address, signed=False) for address in self._addresses]
        if any(value is None for value in values):
            return None
        return description.formatter(cast(list[int], values))

    @property
    def register_poll_type(self) -> RegisterPollType:
        description = cast(DiscoveredTextSensorDescription, self.entity_description)
        return RegisterPollType.ON_CONNECTION if description.poll_once else RegisterPollType.PERIODICALLY


@dataclass(kw_only=True, **ENTITY_DESCRIPTION_KWARGS)
class DiscoveredTextSensorDescription(ModbusSensorDescription):  # type: ignore[misc]
    """Sensor which shows registers decoded as text. Addresses are in register order, not low-order word first"""

    formatter: Callable[[list[int]], str | None]
    poll_once: bool = False

    def create_entity_if_supported(
        self,
        controller: EntityController,
        inverter_model: Inv,
        register_type: RegisterType,
    ) -> Entity | None:
        addresses = self._addresses_for_inverter_model(self.addresses, inverter_model, register_type)
        return _TextSensor(controller, self, addresses, None) if addresses is not None else None


def _code(table: dict[int, str]) -> Callable[[list[int]], str | None]:
    return lambda values: table.get(values[0], f"Unknown ({values[0]})")


def _bcu_version(values: list[int]) -> str:
    # e.g. 0x010D -> 1.013 (EP11 BMS version as shown by the FoxESS cloud)
    return f"{(values[0] >> 8) & 0xF}.{values[0] & 0xFF:03d}"


def _protocol_version(values: list[int]) -> str:
    # four bytes, e.g. 0x0105 0x0300 -> V1.05.03.00
    high, low = values
    return f"V{high >> 8:X}.{high & 0xFF:02X}.{low >> 8:02X}.{low & 0xFF:02X}"


def _date_time(values: list[int]) -> str:
    # The inverter's own clock; its time zone isn't documented, so this is shown as is
    year, month, day, hour, minute, second = values
    return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"


# Grid standard codes, FoxESS Modbus definition V1.05.04.00, table 4-2
_GRID_STANDARDS: dict[int, str] = {
    0: "AS4777_AU (Australia)",
    1: "AS4777_NZ (New Zealand)",
    2: "G98_UK (U.K.)",
    3: "G99_UK (U.K.)",
    4: "EN50549_NL (Netherlands)",
    5: "CEI021_A (Italy)",
    6: "VDE0126 (Germany)",
    7: "VDE4105_DE (Germany)",
    8: "NBR-220_BR (Brazil)",
    9: "NBR-240_BR (Brazil)",
    10: "IEC61727 (India)",
    11: "Philippines",
    12: "NRS_SA (South Africa)",
    13: "Vietnam",
    14: "EN50549_PL (Poland)",
    15: "EN50549_PT (Portugal)",
    16: "PPDS_CR (Czech Republic)",
    17: "UNE-206_SP (Spain)",
    18: "RD1699_SP (Spain)",
    19: "Belgium",
    20: "VFR2019_FR (France)",
    21: "UTE_FR (France)",
    22: "Singapore",
    23: "Indonesia",
    24: "Malaysia",
    25: "Cambodia",
    26: "PEA_TH (Thailand)",
    27: "MEA_TH (Thailand)",
    28: "Sri Lanka",
    29: "Pakistan",
    30: "Ireland",
    31: "Denmark 3.2.1 (Denmark)",
    32: "Slovakia",
    33: "Austria",
    34: "Switzerland",
    35: "Slovenia (slovenia)",
    36: "Hungary",
    37: "Serbia",
    38: "Croatia",
    39: "Turkey (Türkiye)",
    40: "Cyprus",
    41: "Bulgaria",
    42: "Romania",
    43: "Greece",
    44: "Latvia",
    45: "Lithuania",
    46: "Estonia",
    47: "Sweden",
    48: "Norway",
    49: "Finland",
    50: "Argentina",
    51: "Chile BT (Chile)",
    52: "Mexico",
    53: "USA",
    54: "Hawaii (Canada)",
    55: "CQC_CN (China)",
    56: "Japan",
    57: "CQC_CN-1 (China (wide range))",
    58: "Local (India (wide range))",
    59: "Saudi Arabia",
    60: "AS4777_AU-2020A (Australia(A))",
    61: "AS4777_AU-2020B (Australia(B))",
    62: "AS4777_AU-2020C (Australia(C))",
    63: "AS4777_NZ-2020 (New Zealand)",
    64: "CQC_CN-2 (China (wide range 2))",
    65: "CEI021_B (Italy)",
    66: "CEI021_Areti_A (Italy)",
    67: "CEI021_Areti_B (Italy)",
    68: "NBR-220_BR2022 (Brazil)",
    69: "Spain",
    70: "CQC_CN-3 (China)",
    71: "Puerto Rico",
    72: "G98_NI (Northern Ireland)",
    73: "G99_NI (Northern Ireland)",
    74: "USA-208 (USA)",
    75: "VDE4110_DE (Germany)",
    76: "KSC8564 (South Korea)",
    77: "KSC8565 (South Korea)",
    78: "PR-LUMA (Puerto Rico)",
    79: "CEI016 (Italy)",
    80: "DUBAI (Dubai)",
    81: "Denmark3.2.2 (Denmark)",
    82: "TR 3.3.1-DK1 (Denmark)",
    83: "TR 3.3.1-DK2 (Denmark)",
    84: "Chile MT-A (Chile)",
    85: "Chile MT- B (Chile)",
    86: "EN50549_FR (France)",
    87: "NBR-127_BR2022 (Brazil)",
    88: "NBR-W220BR2022 (Brazil)",
    89: "TWN-T (Taiwan, China)",
    90: "TWN-S (Taiwan, China)",
    91: "Israel",
    92: "EN50549_FR_W (France)",
    93: "Test-50Hz (General)",
    94: "Test-60Hz (General)",
    95: "CQC_CN-4 (China)",
    96: "EN 50549-2 (Europe)",
    97: "CQC_CN-5 (China)",
}


def _text(
    key: str,
    addresses: list[int],
    name: str,
    formatter: Callable[[list[int]], str | None],
    *,
    poll_once: bool = False,
) -> DiscoveredTextSensorDescription:
    return DiscoveredTextSensorDescription(
        key=key,
        addresses=[ModbusAddressesSpec(holding=addresses, models=Inv.H3_193)],
        name=name,
        formatter=formatter,
        poll_once=poll_once,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    )


_DECODED: list[EntityFactory] = [
    _text(
        "bms1_master_version",
        [37003],
        "BMS1 Master Version (37003)",
        _bcu_version,
        poll_once=True,
    ),
    _text(
        "modbus_protocol_version",
        [39000, 39001],
        "Modbus Protocol Version (39000)",
        _protocol_version,
        poll_once=True,
    ),
    _text(
        "eps_frequency_select",
        [46612],
        "EPS Frequency (46612)",
        _code({1: "50 Hz", 2: "60 Hz"}),
    ),
    _text(
        "eps_output_mode",
        [46613],
        "EPS Output (46613)",
        _code({0: "Disabled", 2: "EPS Mode", 3: "UPS Mode"}),
    ),
    _text("grid_standard", [49079], "Grid Standard (49079)", _code(_GRID_STANDARDS)),
    _text(
        "meter1_ct1_type",
        [49207],
        "Meter1 / CT1 Type (49207)",
        _code({0: "Off", 1: "Meter 1-phase", 2: "CT", 3: "Meter 3-phase"}),
    ),
    _text(
        "inverter_date_time",
        [49222, 49223, 49224, 49225, 49226, 49227],
        "Inverter Date / Time (49222)",
        _date_time,
    ),
    DiscoveredRegisterSensorDescription(
        key="time_group_1_max_soc_from_grid",
        addresses=[ModbusAddressesSpec(holding=[48014], models=Inv.H3_193)],
        name="Time Group 1 Max SoC From Grid (48014)",
        native_unit_of_measurement="%",
        signed=False,
        post_process=lambda value: float(int(value) >> 8),
        entity_registry_enabled_default=False,
    ),
    DiscoveredRegisterSensorDescription(
        key="time_group_1_min_soc_on_grid",
        addresses=[ModbusAddressesSpec(holding=[48014], models=Inv.H3_193)],
        name="Time Group 1 Min SoC On Grid (48014)",
        native_unit_of_measurement="%",
        signed=False,
        post_process=lambda value: float(int(value) & 0xFF),
        entity_registry_enabled_default=False,
    ),
]


def _named(
    _address: int,
    addresses: list[int],
    name: str,
    *,
    key: str,
    unit: str | None,
    device_class: Any,
    state_class: Any,
    scale: float | None,
    signed: bool,
    poll_once: bool,
) -> DiscoveredRegisterSensorDescription:
    return DiscoveredRegisterSensorDescription(
        key=key,
        addresses=[ModbusAddressesSpec(holding=addresses, models=Inv.H3_193)],
        name=name,
        native_unit_of_measurement=unit,
        device_class=device_class,
        state_class=state_class,
        scale=scale,
        signed=signed,
        poll_once=poll_once,
        entity_registry_enabled_default=False,
    )


def _raw(address: int, addresses: list[int], *, poll_once: bool) -> DiscoveredRegisterSensorDescription:
    return DiscoveredRegisterSensorDescription(
        key=f"register_{address}_raw",
        addresses=[ModbusAddressesSpec(holding=addresses, models=Inv.H3_193)],
        name=f"Register {address} raw",
        signed=False,
        poll_once=poll_once,
        raw=True,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    )


def _developer(
    addresses: list[int],
    name: str,
    *,
    key: str,
    unit: str | None = None,
    scale: float | None = None,
    signed: bool = False,
) -> DiscoveredRegisterSensorDescription:
    """Behind the raw register option like _raw, but named: for comparing against a legacy entity over time"""
    return DiscoveredRegisterSensorDescription(
        key=key,
        addresses=[ModbusAddressesSpec(holding=addresses, models=Inv.H3_193)],
        name=name,
        native_unit_of_measurement=unit,
        scale=scale,
        signed=signed,
        raw=True,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    )


_NAMED = [
    _named(
        37633,
        [37633],
        "BMS1 FCC Capacity (37633)",
        key="reg_37633_bms1_fcc_capacity",
        unit="Ah",
        device_class=None,
        state_class=None,
        scale=0.1,
        signed=False,
        poll_once=True,
    ),
    _named(
        37635,
        [37635],
        "BMS1 Design Energy (37635)",
        key="reg_37635_bms1_design_energy",
        unit="Wh",
        device_class=SensorDeviceClass.ENERGY,
        # A capacity, not an accumulating counter
        state_class=None,
        scale=10.0,
        signed=False,
        poll_once=True,
    ),
    _named(
        38802,
        [38803, 38802],
        "Grid CT1 R Phase Voltage (38802)",
        key="reg_38802_grid_ct1_r_phase_voltage",
        unit="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38804,
        [38805, 38804],
        "Grid CT1 S Phase Voltage (38804)",
        key="reg_38804_grid_ct1_s_phase_voltage",
        unit="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38806,
        [38807, 38806],
        "Grid CT1 T Phase Voltage (38806)",
        key="reg_38806_grid_ct1_t_phase_voltage",
        unit="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38808,
        [38809, 38808],
        "Grid CT1 R Phase Current (38808)",
        key="reg_38808_grid_ct1_r_phase_current",
        unit="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.001,
        signed=True,
        poll_once=False,
    ),
    _named(
        38810,
        [38811, 38810],
        "Grid CT1 S Phase Current (38810)",
        key="reg_38810_grid_ct1_s_phase_current",
        unit="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.001,
        signed=True,
        poll_once=False,
    ),
    _named(
        38812,
        [38813, 38812],
        "Grid CT1 T Phase Current (38812)",
        key="reg_38812_grid_ct1_t_phase_current",
        unit="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.001,
        signed=True,
        poll_once=False,
    ),
    _named(
        38822,
        [38823, 38822],
        "Grid CT1 Combined Reactive (38822)",
        key="reg_38822_grid_ct1_combined_reactive",
        unit="var",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38824,
        [38825, 38824],
        "Grid CT1 R Phase Reactive (38824)",
        key="reg_38824_grid_ct1_r_phase_reactive",
        unit="var",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38826,
        [38827, 38826],
        "Grid CT1 S Phase Reactive (38826)",
        key="reg_38826_grid_ct1_s_phase_reactive",
        unit="var",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38828,
        [38829, 38828],
        "Grid CT1 T Phase Reactive (38828)",
        key="reg_38828_grid_ct1_t_phase_reactive",
        unit="var",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38830,
        [38831, 38830],
        "Grid CT1 Combined Apparent (38830)",
        key="reg_38830_grid_ct1_combined_apparent",
        unit="VA",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38832,
        [38833, 38832],
        "Grid CT1 R Phase Apparent (38832)",
        key="reg_38832_grid_ct1_r_phase_apparent",
        unit="VA",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38834,
        [38835, 38834],
        "Grid CT1 S Phase Apparent (38834)",
        key="reg_38834_grid_ct1_s_phase_apparent",
        unit="VA",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38836,
        [38837, 38836],
        "Grid CT1 T Phase Apparent (38836)",
        key="reg_38836_grid_ct1_t_phase_apparent",
        unit="VA",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        38846,
        [38847, 38846],
        "Grid CT1 Freq (38846)",
        key="reg_38846_grid_ct1_freq",
        unit="Hz",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.01,
        signed=True,
        poll_once=False,
    ),
    _named(
        39051,
        [39051],
        "Number of strings (39051)",
        key="reg_39051_number_of_strings",
        unit=None,
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=True,
    ),
    _named(
        39052,
        [39052],
        "Number of MPPTs (39052)",
        key="reg_39052_number_of_mppts",
        unit=None,
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=True,
    ),
    _named(
        39053,
        [39054, 39053],
        "Rated power (Pn) (39053)",
        key="reg_39053_rated_power_pn",
        unit="kW",
        device_class=SensorDeviceClass.POWER,
        state_class=None,
        scale=0.001,
        signed=True,
        poll_once=True,
    ),
    _named(
        39055,
        [39056, 39055],
        "Maximum active power (Pmax) (39055)",
        key="reg_39055_maximum_active_power_pmax",
        unit="kW",
        device_class=SensorDeviceClass.POWER,
        state_class=None,
        scale=0.001,
        signed=True,
        poll_once=True,
    ),
    _named(
        39057,
        [39058, 39057],
        "Max apparent power (Smax) (39057)",
        key="reg_39057_max_apparent_power_smax",
        unit="kVA",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=None,
        scale=0.001,
        signed=True,
        poll_once=True,
    ),
    _named(
        39059,
        [39060, 39059],
        "Max reactive power fed (Qmax) (39059)",
        key="reg_39059_max_reactive_power_fed_qmax",
        unit="kvar",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=None,
        scale=0.001,
        signed=True,
        poll_once=True,
    ),
    _named(
        39061,
        [39062, 39061],
        "Max reactive power absorbed (Qmax) (39061)",
        key="reg_39061_max_reactive_power_absorbed_qmax",
        unit="kvar",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=None,
        scale=0.001,
        signed=True,
        poll_once=True,
    ),
    _named(
        39118,
        [39119, 39118],
        "Total PV Input Power (39118)",
        key="reg_39118_total_pv_input_power",
        unit="kW",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.001,
        signed=True,
        poll_once=False,
    ),
    _named(
        39149,
        [39150, 39149],
        "Cumulative power generation (39149)",
        key="reg_39149_cumulative_power_generation",
        unit="kWh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        scale=0.01,
        signed=False,
        poll_once=False,
    ),
    _named(
        39151,
        [39152, 39151],
        "Power generation on the day (39151)",
        key="reg_39151_power_generation_on_the_day",
        unit="kWh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        scale=0.01,
        signed=False,
        poll_once=False,
    ),
    _named(
        39216,
        [39217, 39216],
        "EPS Combined Power (39216)",
        key="reg_39216_eps_combined_power",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        39219,
        [39220, 39219],
        "Load R Phase Power (39219)",
        key="reg_39219_load_r_phase_power",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        39221,
        [39222, 39221],
        "Load S Phase Power (39221)",
        key="reg_39221_load_s_phase_power",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        39223,
        [39224, 39223],
        "Load T Phase Power (39223)",
        key="reg_39223_load_t_phase_power",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        39225,
        [39226, 39225],
        "Load Combined Power (39225)",
        key="reg_39225_load_combined_power",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        39270,
        [39271, 39270],
        "Combined Apparent (39270)",
        key="reg_39270_combined_apparent",
        unit="VA",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        39272,
        [39272],
        "INV Frequency R (39272)",
        key="reg_39272_inv_frequency_r",
        unit="Hz",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.01,
        signed=True,
        poll_once=False,
    ),
    _named(
        39273,
        [39273],
        "INV Frequency S (39273)",
        key="reg_39273_inv_frequency_s",
        unit="Hz",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.01,
        signed=True,
        poll_once=False,
    ),
    _named(
        39274,
        [39274],
        "INV Frequency T (39274)",
        key="reg_39274_inv_frequency_t",
        unit="Hz",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.01,
        signed=True,
        poll_once=False,
    ),
    _named(
        39275,
        [39276, 39275],
        "Available Import Power (39275)",
        key="reg_39275_available_import_power",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        39277,
        [39278, 39277],
        "Available Export Power (39277)",
        key="reg_39277_available_export_power",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        39327,
        [39327],
        "MPPT1 Voltage (39327)",
        key="reg_39327_mppt1_voltage",
        unit="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        39328,
        [39328],
        "MPPT1 Current (39328)",
        key="reg_39328_mppt1_current",
        unit="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.01,
        signed=True,
        poll_once=False,
    ),
    _named(
        39329,
        [39330, 39329],
        "MPPT1 Power (39329)",
        key="reg_39329_mppt1_power",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        39331,
        [39331],
        "MPPT2 Voltage (39331)",
        key="reg_39331_mppt2_voltage",
        unit="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        39332,
        [39332],
        "MPPT2 Current (39332)",
        key="reg_39332_mppt2_current",
        unit="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.01,
        signed=True,
        poll_once=False,
    ),
    _named(
        39333,
        [39334, 39333],
        "MPPT2 Power (39333)",
        key="reg_39333_mppt2_power",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        46002,
        [46002],
        "Remote Timeout_Set (46002)",
        key="reg_46002_remote_timeout_set",
        unit="s",
        device_class=SensorDeviceClass.DURATION,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        46003,
        [46004, 46003],
        "Control Active Power (46003)",
        key="reg_46003_control_active_power",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=None,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        46005,
        [46006, 46005],
        "Control Reactive Power (46005)",
        key="reg_46005_control_reactive_power",
        unit="var",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=None,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        46007,
        [46007],
        "Remote Timeout Countdown (46007)",
        key="reg_46007_remote_timeout_countdown",
        unit="s",
        device_class=SensorDeviceClass.DURATION,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        46018,
        [46019, 46018],
        "Pwr_limit Bat_Up (46018)",
        key="reg_46018_pwr_limit_bat_up",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        46020,
        [46021, 46020],
        "Pwr_limit Bat_Dn (46020)",
        key="reg_46020_pwr_limit_bat_dn",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        46503,
        [46503],
        "Threshold SOC (46503)",
        key="reg_46503_threshold_soc",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        46504,
        [46505, 46504],
        "Export Peak Limit (46504)",
        key="reg_46504_export_peak_limit",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=None,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        46607,
        [46607],
        "Max charging current setting (46607)",
        key="reg_46607_max_charging_current_setting",
        unit="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=None,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        46608,
        [46608],
        "Max discharge current setting (46608)",
        key="reg_46608_max_discharge_current_setting",
        unit="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=None,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        46609,
        [46609],
        "Minimum SoC (46609)",
        key="reg_46609_minimum_soc",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        46610,
        [46610],
        "Maximum SoC (46610)",
        key="reg_46610_maximum_soc",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        46611,
        [46611],
        "Minimum SoC OnGrid (46611)",
        key="reg_46611_minimum_soc_ongrid",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        46616,
        [46617, 46616],
        "Export Power Limit (46616)",
        key="reg_46616_export_power_limit",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=None,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        46618,
        [46618],
        "Import Current Limit (46618)",
        key="reg_46618_import_current_limit",
        unit="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=None,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        46619,
        [46619],
        "Export Current Limit (46619)",
        key="reg_46619_export_current_limit",
        unit="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=None,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        46620,
        [46620],
        "Maximum SoC From Grid (46620)",
        key="reg_46620_maximum_soc_from_grid",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        48015,
        [48015],
        "Time Group (N) FC/FDSOC (48015)",
        key="reg_48015_time_group_n_fc_fdsoc",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        48016,
        [48016],
        "Time Group (N) FC/FDPWR (48016)",
        key="reg_48016_time_group_n_fc_fdpwr",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        49007,
        [49007],
        "Active power percentage (49007)",
        key="reg_49007_active_power_percentage",
        unit="%",
        device_class=None,
        state_class=None,
        scale=0.1,
        signed=True,
        poll_once=False,
    ),
    _named(
        49008,
        [49009, 49008],
        "Fixed active power (dispatch) (49008)",
        key="reg_49008_fixed_active_power_dispatch",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        49010,
        [49011, 49010],
        "Night Reactive power (49010)",
        key="reg_49010_night_reactive_power",
        unit="kvar",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=None,
        scale=0.001,
        signed=True,
        poll_once=False,
    ),
    _named(
        49136,
        [49137, 49136],
        "Grid point power limit (49136)",
        key="reg_49136_grid_point_power_limit",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=None,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        49221,
        [49221],
        "Brightness Level (49221)",
        key="reg_49221_brightness_level",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        49230,
        [49230],
        "Idle Loadpower Threshold (49230)",
        key="reg_49230_idle_loadpower_threshold",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        49243,
        [49243],
        "K1 Power Ratio (49243)",
        key="reg_49243_k1_power_ratio",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        49244,
        [49244],
        "K2 Power Ratio (49244)",
        key="reg_49244_k2_power_ratio",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        49245,
        [49245],
        "K3 Power Ratio (49245)",
        key="reg_49245_k3_power_ratio",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        49246,
        [49246],
        "K4 Power Ratio (49246)",
        key="reg_49246_k4_power_ratio",
        unit="%",
        device_class=None,
        state_class=None,
        scale=None,
        signed=False,
        poll_once=False,
    ),
    _named(
        49248,
        [49248],
        "Meter Compensation (49248)",
        key="reg_49248_meter_compensation",
        unit="W",
        device_class=SensorDeviceClass.POWER,
        state_class=None,
        scale=None,
        signed=True,
        poll_once=False,
    ),
    _named(
        49249,
        [49249],
        "GFCI Current (49249)",
        key="reg_49249_gfci_current",
        unit="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.01,
        signed=True,
        poll_once=False,
    ),
]

# The legacy H3_193 entities which stay on their old address on purpose, next to their new-map counterparts, so the
# two can be compared over time (see H3_legacy_uj_cim_megfeleltetes.md)
_DEVELOPER = [
    # ambtemp (31033): no documented new address. 39142 is "reserve", read as ambient temperature by the EVO; 0 here
    _developer(
        [39142],
        "Ambient Temperature candidate (39142)",
        key="reg_39142_ambtemp_candidate",
        unit="°C",
        scale=0.1,
        signed=True,
    ),
    # bms_max_current (31039): undocumented 37615 read the same 14 A
    _developer(
        [37615],
        "BMS Max Current candidate (37615)",
        key="reg_37615_bms_max_current_candidate",
        unit="A",
        scale=0.1,
    ),
    # inverter_fault_code (31044-31051): the documented new alarm and BMS fault words, and the legacy words themselves
    *(_developer([a], f"Alarm {i} ({a})", key=f"reg_{a}_alarm_{i}") for i, a in enumerate(range(39067, 39070), 1)),
    *(
        _developer([a], f"BMS1 Fault{i} ({a})", key=f"reg_{a}_bms1_fault{i}")
        for i, a in enumerate(range(37626, 37632), 1)
    ),
    *(
        _developer([a], f"Legacy Fault Word ({a})", key=f"reg_{a}_legacy_fault_word")
        for a in (31044, 31045, 31047, 31048, 31049, 31050, 31051)
    ),
]

_RAW = [
    _raw(37004, [37004], poll_once=True),
    _raw(37032, [37032], poll_once=True),
    _raw(37033, [37033], poll_once=True),
    _raw(37034, [37034], poll_once=True),
    _raw(37636, [37636], poll_once=False),
    _raw(38801, [38801], poll_once=False),
    _raw(39050, [39050], poll_once=True),
    _raw(39134, [39135, 39134], poll_once=False),
    _raw(39136, [39137, 39136], poll_once=False),
    _raw(39138, [39138], poll_once=False),
    _raw(39162, [39163, 39162], poll_once=False),
    _raw(39168, [39169, 39168], poll_once=False),
    _raw(39256, [39257, 39256], poll_once=False),
    _raw(39258, [39259, 39258], poll_once=False),
    _raw(39260, [39261, 39260], poll_once=False),
    _raw(46001, [46001], poll_once=False),
    _raw(46506, [46506], poll_once=False),
    _raw(46507, [46507], poll_once=False),
    _raw(46508, [46508], poll_once=False),
    _raw(46509, [46509], poll_once=False),
    _raw(46510, [46510], poll_once=False),
    _raw(46511, [46511], poll_once=False),
    _raw(46512, [46512], poll_once=False),
    _raw(46513, [46513], poll_once=False),
    _raw(46514, [46514], poll_once=False),
    _raw(46614, [46614], poll_once=False),
    _raw(46615, [46615], poll_once=False),
    _raw(48000, [48000], poll_once=False),
    _raw(48010, [48010], poll_once=False),
    _raw(48011, [48011], poll_once=False),
    _raw(48012, [48012], poll_once=False),
    _raw(48013, [48013], poll_once=False),
    _raw(49000, [49001, 49000], poll_once=False),
    _raw(49005, [49005], poll_once=False),
    _raw(49006, [49006], poll_once=False),
    _raw(49077, [49077], poll_once=False),
    _raw(49078, [49078], poll_once=False),
    _raw(49206, [49206], poll_once=False),
    _raw(49209, [49209], poll_once=False),
    _raw(49210, [49210], poll_once=False),
    _raw(49211, [49211], poll_once=False),
    _raw(49212, [49212], poll_once=False),
    _raw(49228, [49228], poll_once=False),
    _raw(49229, [49229], poll_once=False),
    _raw(49240, [49240], poll_once=False),
    _raw(49241, [49241], poll_once=False),
    _raw(49242, [49242], poll_once=False),
    _raw(49247, [49247], poll_once=False),
]

_SPEC_FIELDS = ("addresses", "address", "models")


def _specs(description: EntityFactory) -> Iterable[Any]:
    for field_name in _SPEC_FIELDS:
        specs = getattr(description, field_name, None)
        if isinstance(specs, list):
            yield from (s for s in specs if hasattr(s, "_models"))


def _supports(description: EntityFactory, model: Inv) -> bool:
    return any(spec._models & model for spec in _specs(description))  # noqa: SLF001


def _without_h3_193(description: EntityFactory) -> EntityFactory:
    """Copy of the description which no longer applies to Inv.H3_193"""
    changes = {}
    for field_name in _SPEC_FIELDS:
        specs = getattr(description, field_name, None)
        if not isinstance(specs, list) or not any(hasattr(s, "_models") for s in specs):
            continue
        new_specs = []
        for spec in specs:
            if spec._models & Inv.H3_193:  # noqa: SLF001
                spec = copy.copy(spec)
                spec._models = spec._models & ~Inv.H3_193  # noqa: SLF001
                if not spec._models:  # noqa: SLF001
                    continue
            new_specs.append(spec)
        changes[field_name] = new_specs
    return replace(description, **changes) if changes else description  # type: ignore[type-var]


def _h3_smart_holding(description: ModbusSensorDescription) -> list[int]:
    for spec in description.addresses:
        if spec._models & Inv.H3_SMART:  # noqa: SLF001
            addresses = spec.addresses_for_inverter_model(register_type=RegisterType.HOLDING, models=Inv.H3_SMART)
            if addresses:
                return addresses
    raise AssertionError(f"{description.key} has no H3-Smart holding addresses")


def _template(templates: dict[str, EntityFactory], key: str) -> Any:
    template = templates.get(key)
    assert template is not None, f"No template for {key}"
    return template


def apply_discovered_registers(
    entities: Iterable[EntityFactory],
) -> list[EntityFactory]:
    """Adjust the entity list for Inv.H3_193 and add the discovered registers"""
    result: list[EntityFactory] = []
    swapped: set[str] = set()
    ported: set[str] = set()
    smart_templates: dict[str, EntityFactory] = {}
    pro_templates: dict[str, EntityFactory] = {}

    for description in entities:
        key = cast(EntityDescription, description).key
        if (
            key not in smart_templates
            and _supports(description, Inv.H3_SMART)
            and (
                (key in _FROM_H3_SMART and isinstance(description, ModbusSensorDescription))
                or (key == "inverter_state" and isinstance(description, ModbusG2InverterStateSensorDescription))
            )
        ):
            smart_templates[key] = description
        if key in _POWER_FACTOR and key not in pro_templates and _supports(description, Inv.H3_PRO_SET):
            pro_templates[key] = description

        if not _supports(description, Inv.H3_193):
            result.append(description)
            continue

        if key in _REMOVE:
            result.append(_without_h3_193(description))
        elif key in _SWAPS and isinstance(description, ModbusSensorDescription) and key not in swapped:
            addresses, scale, signed = _SWAPS[key]
            result.append(_without_h3_193(description))
            swap_changes: dict[str, Any] = {}
            if getattr(description, "bms_connect_state_address", None) is not None:
                # 37002: 0 init, 1 OK, 2 NG, the same meaning ModbusBatterySensor expects
                swap_changes["bms_connect_state_address"] = [ModbusAddressSpec(holding=37002, models=Inv.H3_193)]
            result.append(
                replace(
                    description,
                    addresses=[ModbusAddressesSpec(holding=addresses, models=Inv.H3_193)],
                    scale=scale,
                    signed=signed,
                    **swap_changes,
                )
            )
            swapped.add(key)
        elif key in _VERSIONS and isinstance(description, ModbusVersionSensorDescription):
            address, is_hex = _VERSIONS[key]
            result.append(_without_h3_193(description))
            result.append(
                replace(
                    description,
                    address=[ModbusAddressSpec(holding=address, models=Inv.H3_193)],
                    is_hex=is_hex,
                )
            )
            ported.add(key)
        elif key in _WRITABLE_PORTS and hasattr(description, "addresses"):
            # Both the writable number and the read-only sensor with the same key
            changes: dict[str, Any] = {
                "addresses": [ModbusAddressesSpec(holding=_WRITABLE_PORTS[key], models=Inv.H3_193)]
            }
            if isinstance(description, ModbusSensorDescription) and key in _WRITABLE_PORT_SIGNED:
                changes["signed"] = _WRITABLE_PORT_SIGNED[key]
            result.append(_without_h3_193(description))
            result.append(replace(description, **changes))  # type: ignore[type-var]
            ported.add(key)
        elif key in _SELECT_PORTS and hasattr(description, "options_map"):
            address, options_map = _SELECT_PORTS[key]
            result.append(_without_h3_193(description))
            legacy_options = description.options_map
            result.append(
                replace(
                    description,  # type: ignore[type-var]
                    address=[ModbusAddressSpec(holding=address, models=Inv.H3_193)],
                    options_map=options_map if options_map is not None else legacy_options,
                )
            )
            ported.add(key)
        else:
            result.append(description)

    missing = set(_SWAPS) - swapped
    assert not missing, f"Swaps without an H3_193 entity: {missing}"
    missing = (set(_VERSIONS) | set(_WRITABLE_PORTS) | set(_SELECT_PORTS)) - ported
    assert not missing, f"Ports without an H3_193 entity: {missing}"

    for key in _FROM_H3_SMART:
        template = cast(ModbusSensorDescription, _template(smart_templates, key))
        changes = {}
        if isinstance(template, ModbusBatterySensorDescription):
            connect_address = template._address_for_inverter_model(  # noqa: SLF001
                template.bms_connect_state_address, Inv.H3_SMART, RegisterType.HOLDING
            )
            assert connect_address is not None, f"{key} has no H3-Smart BMS connection address"
            changes["bms_connect_state_address"] = [ModbusAddressSpec(holding=connect_address, models=Inv.H3_193)]
        result.append(
            replace(
                template,
                addresses=[ModbusAddressesSpec(holding=_h3_smart_holding(template), models=Inv.H3_193)],
                entity_registry_enabled_default=False,
                signed=_TEMPLATE_SIGNED.get(key, template.signed),
                **changes,
            )
        )

    for key, addresses in _POWER_FACTOR.items():
        result.append(
            replace(
                cast(ModbusSensorDescription, _template(pro_templates, key)),
                addresses=[ModbusAddressesSpec(holding=addresses, models=Inv.H3_193)],
                scale=_POWER_FACTOR_SCALE,
                entity_registry_enabled_default=False,
            )
        )

    result.append(
        replace(
            cast(
                ModbusG2InverterStateSensorDescription,
                _template(smart_templates, "inverter_state"),
            ),
            addresses=[ModbusAddressesSpec(holding=_INVERTER_STATE_ADDRESSES, models=Inv.H3_193)],
        )
    )

    result.extend(_DECODED)
    result.extend(_NAMED)
    result.extend(_DEVELOPER)
    result.extend(_RAW)
    return apply_entity_nomenclature(_add_unified_map(result))


# EXPERIMENTAL unified map (Inv.UNIFIED_SET): the H3_193 entities which only use the new map. Read-only for now: the
# writable ranges differ per family (e.g. KH [0, 50] A, H1 [0, 40] A for 46607/46608), so no numbers, selects or
# remote control.
_UNIFIED_SPEC_FIELDS = ("addresses", "address", "bms_connect_state_address")
# Taken over from the H3-Smart, whose registers for these are the documented ones: the alarm words (decoded like the
# H3 Pro / H3 Smart / KH 1.33+) and the third PV string, which the H3_193 set doesn't have
_UNIFIED_FROM_H3_SMART = {
    "inverter_fault_code",
    "pv3_voltage",
    "pv3_current",
    "pv3_power",
    "pv3_energy_total",
}


def _is_new_map_address(address: int) -> bool:
    return address >= 36000 and not 40000 <= address <= 44999


def _is_phase_s_or_t(key: str) -> bool:
    return key.endswith(("_S", "_T", "_frequency_s", "_frequency_t")) or any(
        f"_{phase}_phase_" in key for phase in "st"
    )


_ModelSpecT = TypeVar("_ModelSpecT", bound=ModbusAddressSpecBase | EntitySpec)


def _with_models(spec: _ModelSpecT, models: Inv) -> _ModelSpecT:
    spec = copy.copy(spec)
    spec._models = spec._models | models  # noqa: SLF001
    return spec


def _add_unified_map(entities: list[EntityFactory]) -> list[EntityFactory]:
    result: list[EntityFactory] = []
    unified_keys: set[str] = set()
    for description in entities:
        key = cast(EntityDescription, description).key
        unified = Inv.UNIFIED_3PH if _is_phase_s_or_t(key) else Inv.UNIFIED_SET
        if key in _UNIFIED_FROM_H3_SMART and _supports(description, Inv.H3_SMART):
            field = "models" if isinstance(description, ModbusIntegrationSensorDescription) else "addresses"
            smart_specs = getattr(description, field)
            assert all(
                _is_new_map_address(a)
                for spec in smart_specs
                for a in spec.addresses_for_inverter_model(register_type=RegisterType.HOLDING, models=Inv.H3_SMART)
                or []
            ), key
            new_specs = [
                _with_models(spec, unified) if Inv.H3_SMART in spec._models else spec  # noqa: SLF001
                for spec in smart_specs
            ]
            result.append(replace(cast(Any, description), **{field: new_specs}))
            unified_keys.add(key)
            continue

        specs = {field: getattr(description, field, None) or [] for field in _UNIFIED_SPEC_FIELDS}
        own = [
            spec.addresses_for_inverter_model(register_type=RegisterType.HOLDING, models=Inv.H3_193)
            for spec in specs["addresses"] + specs["address"]
            if isinstance(spec, InverterModelSpec)
        ]
        own = [a for a in own if a is not None]
        connect = [
            spec.addresses_for_inverter_model(register_type=RegisterType.HOLDING, models=Inv.H3_193)
            for spec in specs["bms_connect_state_address"]
        ]
        addresses = [x for a in own + [c for c in connect if c is not None] for x in a]
        if (
            description.entity_type is not SensorEntity
            or not own
            or not addresses
            or not all(_is_new_map_address(a) for a in addresses)
        ):
            result.append(description)
            continue

        changes = {
            field: [
                _with_models(spec, unified)
                if spec.addresses_for_inverter_model(register_type=RegisterType.HOLDING, models=Inv.H3_193) is not None
                else spec
                for spec in value
            ]
            for field, value in specs.items()
            if value
        }
        result.append(replace(cast(Any, description), **changes))
        unified_keys.add(key)

    # Energy integrated from a power entity, where that one is on the unified map
    for i, description in enumerate(result):
        if (
            isinstance(description, ModbusIntegrationSensorDescription)
            and description.source_entity in unified_keys
            and any(Inv.H3_193 in spec._models for spec in description.models)  # noqa: SLF001
        ):
            result[i] = replace(
                description,
                models=[
                    _with_models(spec, Inv.UNIFIED_SET) if Inv.H3_193 in spec._models else spec  # noqa: SLF001
                    for spec in description.models
                ],
            )
    return result
