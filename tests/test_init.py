"""Test the PID controller integration."""

import pytest
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pid_controller.const import (
    CONF_INPUT1,
    CONF_OUTPUT,
    DOMAIN,
)


@pytest.mark.parametrize(
    "platform",
    [
        "number",
    ],
)
async def test_setup_and_remove_config_entry(
    hass: HomeAssistant,
    platform: str,
) -> None:
    """Test setting up and removing a config entry."""
    input_par = "sensor.input"
    output_par = "number.output"

    registry = er.async_get(hass)
    pid_controller_entity_id = f"{platform}.my_pid_controller"

    # Setup the config entry
    config_entry = MockConfigEntry(
        data={},
        domain=DOMAIN,
        options={
            CONF_OUTPUT: output_par,
            CONF_INPUT1: input_par,
            CONF_NAME: "My pid_controller",
        },
        title="My pid_controller",
    )
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Check the entity is registered in the entity registry
    assert registry.async_get(pid_controller_entity_id) is not None

    # Check the platform is setup correctly
    state = hass.states.get(pid_controller_entity_id)
    assert state.state == "0.0"

    # Remove the config entry
    assert await hass.config_entries.async_remove(config_entry.entry_id)
    await hass.async_block_till_done()

    # Check the state and entity registry entry are removed
    assert hass.states.get(pid_controller_entity_id) is None
    assert registry.async_get(pid_controller_entity_id) is None
