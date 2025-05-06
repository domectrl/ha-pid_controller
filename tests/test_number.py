"""The test for the pid_controller number platform."""

import asyncio
import logging

import pytest
from homeassistant.components.number import ATTR_VALUE, SERVICE_SET_VALUE
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_MAXIMUM,
    CONF_MINIMUM,
    CONF_NAME,
    CONF_PLATFORM,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.typing import ConfigType
from homeassistant.setup import async_setup_component
from homeassistant.util.unit_system import METRIC_SYSTEM

from custom_components.pid_controller.const import (
    CONF_INPUT1,
    CONF_INPUT2,
    CONF_OUTPUT,
    CONF_PID_DIR,
    DOMAIN,
    PID_DIR_REVERSE,
)
from custom_components.pid_controller.pid_shared.const import (
    CONF_CYCLE_TIME,
    CONF_PID_KD,
    CONF_PID_KI,
    CONF_PID_KP,
)

_LOGGER = logging.getLogger(__name__)


@pytest.fixture(name="setup_comp")
async def _fixture_setup_comp(hass: HomeAssistant) -> None:
    """Initialize components."""
    hass.config.units = METRIC_SYSTEM
    assert await async_setup_component(hass, "homeassistant", {})
    await hass.async_block_till_done()


async def _setup_controller(  # noqa: PLR0913
    hass: HomeAssistant,
    config: ConfigType,
    input_par: str,
    output_par: str | None,
    input_value: float,
    output_value: float,
) -> None:
    """
    Setupfunctions for the controller.

    The input and output device do really exist, only set state.
    """
    hass.states.async_set(input_par, input_value)
    if output_par:
        hass.states.async_set(output_par, output_value)
    assert await async_setup_component(hass, Platform.NUMBER, config)
    await hass.async_block_till_done()


async def test_pid_controller_turn_on_off(hass: HomeAssistant, setup_comp) -> None:  # noqa: ANN001, ARG001
    """Test turn on and turn off for  pid controller (number), using only Kp: output equals error."""
    input_par = "sensor.input1"
    output_par = "number.output"
    pid = f"{Platform.NUMBER}.pid"

    cycle_time = 0.01  # Cycle time in seconds
    config = {
        Platform.NUMBER: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "pid",
            CONF_INPUT1: input_par,
            CONF_OUTPUT: output_par,
            CONF_PID_KP: 1,
            CONF_PID_KI: 0,
            CONF_PID_KD: 0,
            CONF_CYCLE_TIME: {"seconds": cycle_time},
        }
    }
    await _setup_controller(hass, config, input_par, output_par, 10.0, 0.0)

    # On initialize value is 0, so output should be off. Check all states.
    assert hass.states.get(pid).state == "0.0"
    assert hass.states.get(input_par).state == "10.0"
    assert hass.states.get(output_par).state == "0.0"

    # Now set pid setpoint to value 20. Input remains 10, but pid is not yet turned on,
    # so output state should remain 0.
    await hass.services.async_call(
        Platform.NUMBER,
        SERVICE_SET_VALUE,
        {ATTR_VALUE: 20, ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(output_par).state == "0.0"
    await hass.async_block_till_done()

    # Turn on PID controller. Output should run up after a while to 10
    await hass.services.async_call(
        "pid_controller",
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    # Sleep some cyles.
    await asyncio.sleep(cycle_time * 3)
    # Check if output is equal to 10, as Kp=1
    # and difference between in- and output is 10.
    assert hass.states.get(output_par).state == "10.0"

    # Now test if we can turn the regulator off again
    await hass.async_block_till_done()

    # Turn on PID controller. Output should run up after a while to 10
    await hass.services.async_call(
        "pid_controller",
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    hass.states.async_set(output_par, 0.0)
    await hass.async_block_till_done()
    # Sleep some cyles.
    await asyncio.sleep(cycle_time * 3)
    # Check if output is still equal to 0, as Kp=1
    # and difference between in- and output is 10
    # but retulator was turned off
    assert hass.states.get(output_par).state == "0.0"
    await hass.async_block_till_done()

    await hass.services.async_call(
        "homeassistant",
        "stop",
        None,
        blocking=True,
    )


async def test_pid_controller_kp(hass: HomeAssistant, setup_comp) -> None:  # noqa: ANN001, ARG001
    """Test function Kp for normal pid controller (number): output equals error."""
    input_par = "sensor.input1"
    output_par = "number.output"
    pid = f"{Platform.NUMBER}.pid"

    cycle_time = 0.01  # Cycle time in seconds
    config = {
        Platform.NUMBER: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "pid",
            CONF_INPUT1: input_par,
            CONF_OUTPUT: output_par,
            CONF_PID_KP: 1,
            CONF_PID_KI: 0,
            CONF_PID_KD: 0,
            CONF_CYCLE_TIME: {"seconds": cycle_time},
        }
    }
    await _setup_controller(hass, config, input_par, output_par, 10.0, 0.0)

    # On initialize value is 0, so output should be off. Check all states.
    assert hass.states.get(pid).state == "0.0"
    assert hass.states.get(input_par).state == "10.0"
    assert hass.states.get(output_par).state == "0.0"

    # Now set pid setpoint to value 20. Input remains 10, but pid is not yet turned on,
    # so output state should remain 0.
    await hass.services.async_call(
        Platform.NUMBER,
        SERVICE_SET_VALUE,
        {ATTR_VALUE: 20, ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(output_par).state == "0.0"
    await hass.async_block_till_done()

    # Turn on PID controller. Output should run up after a while to 10
    await hass.services.async_call(
        "pid_controller",
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    # Sleep some cyles.
    await asyncio.sleep(cycle_time * 3)
    # Check if output is equal to 10, as Kp=1
    # and difference between in- and output is 10.
    assert hass.states.get(output_par).state == "10.0"
    await hass.services.async_call(
        "homeassistant",
        "stop",
        None,
        blocking=True,
    )


async def test_pid_controller_kp_reverse(hass: HomeAssistant, setup_comp) -> None:  # noqa: ANN001, ARG001
    """Test function Kp for normal pid controller (number): output equals error."""
    input_par = "sensor.input1"
    output_par = "number.output"
    pid = f"{Platform.NUMBER}.pid"

    # Min/max of the controller are set up by output limits, so assign
    hass.states.async_set(output_par, 0.0)
    state = hass.states.get(output_par)
    attr = state.attributes.copy()
    attr["min"] = -100.0
    attr["max"] = 100.0
    hass.states.async_set(output_par, 0.0, attr)

    cycle_time = 0.01  # Cycle time in seconds
    config = {
        Platform.NUMBER: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "pid",
            CONF_INPUT1: input_par,
            CONF_OUTPUT: output_par,
            CONF_PID_KP: 1,
            CONF_PID_KI: 0,
            CONF_PID_KD: 0,
            CONF_PID_DIR: PID_DIR_REVERSE,
            CONF_CYCLE_TIME: {"seconds": cycle_time},
        }
    }
    await _setup_controller(hass, config, input_par, None, 10.0, 0.0)

    # On initialize value is 0, so output should be off. Check all states.
    assert hass.states.get(pid).state == "0.0"
    assert hass.states.get(input_par).state == "10.0"
    assert hass.states.get(output_par).state == "0.0"

    # Now set pid setpoint to value 20. Input remains 10, but pid is not yet turned on,
    # so output state should remain 0.
    await hass.services.async_call(
        Platform.NUMBER,
        SERVICE_SET_VALUE,
        {ATTR_VALUE: 20, ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(output_par).state == "0.0"

    # Turn on PID controller. Output should run down after a while to -10
    await hass.services.async_call(
        "pid_controller",
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    # Sleep some cyles.
    await asyncio.sleep(cycle_time * 3)
    # Check if output is equal to -10, as Kp=1
    # and difference between in- and output is 10.
    assert hass.states.get(output_par).state == "-10.0"
    # Now invert in- and output; output state should
    # change polarity.
    # Set pid setpoint to value 10.
    await hass.services.async_call(
        Platform.NUMBER,
        SERVICE_SET_VALUE,
        {ATTR_VALUE: 10, ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    # Set input to value 20
    hass.states.async_set(input_par, 20.0)
    # Sleep some cyles.
    await asyncio.sleep(cycle_time * 3)
    # Check if output is equal to 10, as Kp=1
    # and difference between in- and output is -10.
    assert hass.states.get(output_par).state == "10.0"

    await hass.services.async_call(
        "homeassistant",
        "stop",
        None,
        blocking=True,
    )


async def test_pid_controller_kp_differential(hass: HomeAssistant, setup_comp) -> None:  # noqa: ANN001, ARG001
    """Test function Kp for normal pid controller (number): output equals error."""
    input_par = "sensor.input1"
    input2_par = "sensor.input2"
    output_par = "number.output"
    pid = f"{Platform.NUMBER}.pid"

    cycle_time = 0.01  # Cycle time in seconds
    config = {
        Platform.NUMBER: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "pid",
            CONF_INPUT1: input_par,
            CONF_INPUT2: input2_par,
            CONF_OUTPUT: output_par,
            CONF_PID_KP: 1,
            CONF_PID_KI: 0,
            CONF_PID_KD: 0,
            CONF_CYCLE_TIME: {"seconds": cycle_time},
        }
    }
    await _setup_controller(hass, config, input_par, output_par, 10.0, 0.0)
    # Assign input2 value
    hass.states.async_set(input2_par, 12.0)

    # On initialize value is 0, so output should be off. Check all states.
    assert hass.states.get(pid).state == "0.0"
    assert hass.states.get(input_par).state == "10.0"
    assert hass.states.get(input2_par).state == "12.0"
    assert hass.states.get(output_par).state == "0.0"

    # Now set pid setpoint to value 20. Input remains 10, but pid is not yet turned on,
    # so output state should remain 0.
    await hass.services.async_call(
        Platform.NUMBER,
        SERVICE_SET_VALUE,
        {ATTR_VALUE: 20, ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(output_par).state == "0.0"

    # Turn on PID controller. Output should run down after a while to -10
    await hass.services.async_call(
        "pid_controller",
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    # Sleep some cyles.
    await asyncio.sleep(cycle_time * 3)
    # Check if output is equal to 2, as Kp=1
    # and difference between in- two inputs is 2.
    assert hass.states.get(output_par).state == "18.0"
    await hass.services.async_call(
        "homeassistant",
        "stop",
        None,
        blocking=True,
    )


async def test_pid_controller_ki(hass: HomeAssistant, setup_comp) -> None:  # noqa: ANN001, ARG001
    """Test Ki function for normal pid controller (number): output should run to max."""
    input_par = "sensor.input1"
    output_par = "number.output"
    pid = f"{Platform.NUMBER}.pid"
    cycle_time = 0.05  # Cycle time in seconds

    config = {
        Platform.NUMBER: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "pid",
            CONF_INPUT1: input_par,
            CONF_OUTPUT: output_par,
            CONF_PID_KP: 0,
            CONF_PID_KI: 100,
            CONF_PID_KD: 0,
            CONF_CYCLE_TIME: {"seconds": cycle_time},
        }
    }
    await _setup_controller(hass, config, input_par, output_par, 10.0, 0.0)

    # On initialize value is 0, so output should be off. Check all states.
    assert hass.states.get(pid).state == "0.0"
    assert hass.states.get(input_par).state == "10.0"
    assert hass.states.get(output_par).state == "0.0"

    # Now set pid setpoint to value 20. Input remains 10, but pid is not yet turned on,
    # so output state should remain 0.
    await hass.services.async_call(
        Platform.NUMBER,
        SERVICE_SET_VALUE,
        {ATTR_VALUE: 20, ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(output_par).state == "0.0"

    # Turn on PID controller. Output should run up after a while to 100
    # (as that's the max of the output)
    await hass.services.async_call(
        "pid_controller",
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    # Sleep some cyles.
    await asyncio.sleep(cycle_time * 10)
    # Check if output is equal to 100, as Ki=100
    # and difference between in- and output is 10.
    assert hass.states.get(output_par).state == "100.0"
    await hass.services.async_call(
        "homeassistant",
        "stop",
        None,
        blocking=True,
    )
    await asyncio.sleep(cycle_time * 10)


async def test_pid_controller_kd(hass: HomeAssistant, setup_comp) -> None:  # noqa: ANN001, ARG001
    """Test Kd function for normal pid controller (number): output should stay 0."""
    input_par = "sensor.input1"
    output_par = "number.output"
    pid = f"{Platform.NUMBER}.pid"
    cycle_time = 0.01  # Cycle time in seconds

    config = {
        Platform.NUMBER: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "pid",
            CONF_INPUT1: input_par,
            CONF_OUTPUT: output_par,
            CONF_PID_KP: 0,
            CONF_PID_KI: 0,
            CONF_PID_KD: 100,
            CONF_CYCLE_TIME: {"seconds": cycle_time},
        }
    }
    await _setup_controller(hass, config, input_par, output_par, 10.0, 0.0)

    # On initialize value is 0, so output should be off. Check all states.
    assert hass.states.get(pid).state == "0.0"
    assert hass.states.get(input_par).state == "10.0"
    assert hass.states.get(output_par).state == "0.0"

    # Now set pid setpoint to value 20. Input remains 10, but pid is not yet turned on,
    # so output state should remain 0.
    await hass.services.async_call(
        Platform.NUMBER,
        SERVICE_SET_VALUE,
        {ATTR_VALUE: 20, ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(output_par).state == "0.0"

    # Turn on PID controller. Output should run up after a while to 100
    # (as that's the max of the output)
    await hass.services.async_call(
        "pid_controller",
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()
    # Sleep some cyles.
    await asyncio.sleep(cycle_time * 10)
    # Check if output is equal to 0, as we only have a Kd100
    # and  input remains always 10.0
    assert hass.states.get(output_par).state == "0.0"
    await hass.services.async_call(
        "homeassistant",
        "stop",
        None,
        blocking=True,
    )


async def test_output_does_not_exist(hass: HomeAssistant, setup_comp, caplog) -> None:  # noqa: ANN001, ARG001
    """Test output does not exist."""
    input_par = "sensor.input1"
    output_par = "number.output"
    cycle_time = 0.01  # Cycle time in seconds

    # clear logging
    caplog.clear()
    config = {
        Platform.NUMBER: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "pid",
            CONF_INPUT1: input_par,
            CONF_OUTPUT: "DoesNotExist",
            CONF_PID_KP: 1,
            CONF_PID_KI: 0,
            CONF_PID_KD: 0,
            CONF_CYCLE_TIME: {"seconds": cycle_time},
        }
    }
    await _setup_controller(hass, config, input_par, output_par, 10.0, 0.0)

    # test if an error was generated
    assert "ERROR" in caplog.text
    await hass.services.async_call(
        "homeassistant",
        "stop",
        None,
        blocking=True,
    )
    # Sleep some cyles.
    await asyncio.sleep(cycle_time * 10)


async def test_outside_range(hass: HomeAssistant, setup_comp) -> None:  # noqa: ANN001, ARG001
    """Test what happens if we write a value outside the range."""
    input_par = "sensor.input1"
    output_par = "number.output"
    pid = f"{Platform.NUMBER}.pid"
    cycle_time = 0.01  # Cycle time in seconds
    minimum = 20.0
    maximum = 30.0

    config = {
        Platform.NUMBER: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "pid",
            CONF_INPUT1: input_par,
            CONF_OUTPUT: output_par,
            CONF_PID_KP: 1,
            CONF_PID_KI: 0,
            CONF_PID_KD: 0,
            CONF_CYCLE_TIME: {"seconds": cycle_time},
            CONF_MINIMUM: minimum,
            CONF_MAXIMUM: maximum,
        }
    }
    await _setup_controller(hass, config, input_par, output_par, 10.0, 0.0)

    # On initialize value is 0, so output should be off. Check all states.
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(input_par).state == "10.0"
    assert hass.states.get(output_par).state == "0.0"

    # Set value to 5. This should generate a ValueError in the number component
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            Platform.NUMBER,
            SERVICE_SET_VALUE,
            {ATTR_VALUE: 5, ATTR_ENTITY_ID: pid},
            blocking=True,
        )

    await hass.async_block_till_done()
    # Value should not be changed
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(output_par).state == "0.0"

    # Set value to 50. This should generate a ValueError in the number component
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            Platform.NUMBER,
            SERVICE_SET_VALUE,
            {ATTR_VALUE: 50, ATTR_ENTITY_ID: pid},
            blocking=True,
        )

    await hass.async_block_till_done()
    # Value should not be changed
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(output_par).state == "0.0"

    # Turn on PID controller and repeat
    await hass.services.async_call(
        "pid_controller",
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()

    # Set value to 5. This should generate a ValueError in the number component
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            Platform.NUMBER,
            SERVICE_SET_VALUE,
            {ATTR_VALUE: 5, ATTR_ENTITY_ID: pid},
            blocking=True,
        )
    await hass.async_block_till_done()
    await asyncio.sleep(cycle_time * 3)
    # Value should not be changed, except output should regulate to 10 now.
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(output_par).state == "10.0"

    # Set value to 50. This should generate a ValueError in the number component
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            Platform.NUMBER,
            SERVICE_SET_VALUE,
            {ATTR_VALUE: 50, ATTR_ENTITY_ID: pid},
            blocking=True,
        )

    await hass.async_block_till_done()
    await asyncio.sleep(cycle_time * 3)
    # Value should not be changed, except output still regulated to 10 now.
    assert hass.states.get(pid).state == "20.0"
    assert hass.states.get(output_par).state == "10.0"
    # Stop hass
    await hass.services.async_call(
        "homeassistant",
        "stop",
        None,
        blocking=True,
    )
    # Sleep some cyles.
    await asyncio.sleep(cycle_time * 10)


async def test_bad_value(hass: HomeAssistant, setup_comp, caplog) -> None:  # noqa: ANN001, ARG001
    """Test what happens if we send a bad value."""
    input_par = "sensor.input1"
    output_par = "number.output"
    pid = f"{Platform.NUMBER}.pid"
    cycle_time = 0.01  # Cycle time in seconds

    config = {
        Platform.NUMBER: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "pid",
            CONF_INPUT1: input_par,
            CONF_OUTPUT: output_par,
            CONF_PID_KP: 1,
            CONF_PID_KI: 0,
            CONF_PID_KD: 0,
            CONF_CYCLE_TIME: {"seconds": cycle_time},
        }
    }
    await _setup_controller(hass, config, input_par, output_par, 10.0, 0.0)

    # On initialize value is 0, so output should be off. Check all states.
    assert hass.states.get(pid).state == "0.0"
    assert hass.states.get(input_par).state == "10.0"
    assert hass.states.get(output_par).state == "0.0"

    # Set value to "infinity".
    # This should generate an exception, value should remain what it was
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            Platform.NUMBER,
            SERVICE_SET_VALUE,
            {ATTR_VALUE: "inf", ATTR_ENTITY_ID: pid},
            blocking=True,
        )
    assert hass.states.get(pid).state == "0.0"

    # Set value to "nan".
    # This should generate a warning, value should remain what it was
    caplog.clear()
    await hass.services.async_call(
        Platform.NUMBER,
        SERVICE_SET_VALUE,
        {ATTR_VALUE: "nan", ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    assert hass.states.get(pid).state == "0.0"
    # test if a warning was generated
    assert "WARNING" in caplog.text

    # Now repeat with controller turned on
    await hass.services.async_call(
        "pid_controller",
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    await hass.async_block_till_done()

    # Set value to "infinity".
    # This should generate an exception, value should remain what it was
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            Platform.NUMBER,
            SERVICE_SET_VALUE,
            {ATTR_VALUE: "inf", ATTR_ENTITY_ID: pid},
            blocking=True,
        )
    assert hass.states.get(pid).state == "0.0"

    # Set value to "nan".
    # This should generate a warning, value should remain what it was
    caplog.clear()
    await hass.services.async_call(
        Platform.NUMBER,
        SERVICE_SET_VALUE,
        {ATTR_VALUE: "nan", ATTR_ENTITY_ID: pid},
        blocking=True,
    )
    assert hass.states.get(pid).state == "0.0"

    await hass.services.async_call(
        "homeassistant",
        "stop",
        None,
        blocking=True,
    )


# Reload currently does not work!
#
# async def test_reload(hass: HomeAssistant, setup_comp) -> None:
#    """Verify we can reload pid_controller from yaml file."""
#    input = "sensor.input1"
#    output = "number.output"
#    pid = f"{Platform.NUMBER}.pid"
#    cycle_time = 0.01  # Cycle time in seconds
#
#    config = {
#        Platform.NUMBER: {
#            CONF_PLATFORM: DOMAIN,
#            CONF_NAME: "pid",
#            CONF_INPUT1: input,
#            CONF_OUTPUT: output,
#            CONF_PID_KP: 1,
#            CONF_PID_KI: 0,
#            CONF_PID_KD: 0,
#            CONF_CYCLE_TIME: {"seconds": cycle_time},
#        }
#    }
#   await _setup_controller(hass, config, input, output, 10.0, 0.0)#
#
#    # On initialize value is 0, so output should be off. Check all states.
#    assert hass.states.get(pid).state == "0.0"
#    assert hass.states.get(input).state == "10.0"
#    assert hass.states.get(output).state == "0.0"
#    assert len(hass.states.async_all()) == 3
#
#    yaml_path = get_fixture_path("configuration.yaml", "pid_controller")
#    with patch.object(hass_config, "YAML_CONFIG_FILE", yaml_path):
#        await hass.services.async_call(
#            DOMAIN,
#            SERVICE_RELOAD,
#            {},
#            blocking=True,
#        )
#        await hass.async_block_till_done()
#
#    assert len(hass.states.async_all()) == 3
#    assert hass.states.get(pid) is None
#    assert hass.states.get("number.second_test")
