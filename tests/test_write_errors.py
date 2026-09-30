"""A failed write reaches the user as a HomeAssistantError, not as an unknown error."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.foxess_modbus.client.modbus_client import ModbusClientFailedError
from custom_components.foxess_modbus.modbus_controller import ModbusController
from custom_components.foxess_modbus.vendor.pymodbus import ModbusIOException


def _controller(write_registers: AsyncMock) -> ModbusController:
    controller = object.__new__(ModbusController)
    client = MagicMock()
    client.write_registers = write_registers
    controller._client = client  # noqa: SLF001
    controller._slave = 247  # noqa: SLF001
    controller._data = {}  # noqa: SLF001
    return controller


async def test_failed_write_raises_home_assistant_error() -> None:
    error = ModbusClientFailedError("Error writing registers", MagicMock(), ModbusIOException("timeout"))
    controller = _controller(AsyncMock(side_effect=error))
    with pytest.raises(HomeAssistantError, match="Error writing registers") as raised:
        await controller.write_registers(46607, [150])
    assert raised.value.__cause__ is error


async def test_out_of_range_value_raises_home_assistant_error() -> None:
    write = AsyncMock()
    controller = _controller(write)
    with pytest.raises(HomeAssistantError, match="must be between"):
        await controller.write_registers(46607, [70000])
    write.assert_not_called()
