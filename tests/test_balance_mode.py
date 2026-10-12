"""Balance mode for H3 Manager 1.93+."""

from typing import Any

import pytest

from custom_components.foxess_modbus.common.types import Inv
from custom_components.foxess_modbus.common.types import RegisterType
from custom_components.foxess_modbus.entities.entity_descriptions import ENTITIES


def _serialized(inv: Inv) -> dict[tuple[str, str], dict[str, Any]]:
    result = {}
    for factory in ENTITIES:
        serialized = factory.serialize(inv, RegisterType.HOLDING)
        if serialized is not None:
            result[(serialized["type"], serialized["key"])] = serialized
    return result


def test_h3_193() -> None:
    entities = _serialized(Inv.H3_193)
    balance = entities[("select", "balance_mode")]
    assert balance["addresses"] == [46614]
    assert list(balance["values"].values()) == ["Disabled", "Total", "Per Phase"]
    assert balance["read_only_options"] == ["Per Phase"]


@pytest.mark.parametrize("inv", [Inv.H3_180, Inv.H3_PRE180, Inv.AIO_H3_101, Inv.KUARA_H3, Inv.H3_PRO_SET])
def test_other_h3_family_unchanged(inv: Inv) -> None:
    keys = {key for _, key in _serialized(inv)}
    assert "balance_mode" not in keys
