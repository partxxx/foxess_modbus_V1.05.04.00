"""Service helpers must look devices up through the device registry API (see #1262)."""

from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry

from custom_components.foxess_modbus.const import DOMAIN
from custom_components.foxess_modbus.const import FRIENDLY_NAME
from custom_components.foxess_modbus.services import utils


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
