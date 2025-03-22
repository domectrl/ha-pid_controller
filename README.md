# PID Controller integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

This integration contains a PID regulator. The value for an output number entity will be calculated using the [Proportional–Integral–Derivative algorithm (PID)](https://en.wikipedia.org/wiki/PID_controller). 

The implementation of the PID controller contains bumpless operation, and is prevented against integral windup by clipping of the output value to the minimum and maximum of the corresponding output number entity.

This controller is typically useful in regulated systems. For example to regulate the speed of a water pump in a heat collector to keep the temperature difference between the outgoing and incomming water stream on a certain level, so that the heat collector will perform optimally.

Setting up the optimal parameters for a PID controller can be a tough job. Depending on your particular job, you might already know more or less what the parameters should be. If required, you could use [manual tuning](https://en.wikipedia.org/wiki/PID_controller#Manual_tuning) to find optimal parameters. A small summary for PID tuning:
- For kp, start with a small number (1) and gradually make it bigger if you see that the direct reaction of the controller is too low. Increase the kp, until the output oscillates, then set it to half of this value.
- For ki, keep this number to 0 until kp is set. Then, start with a very small number (0.01). If you see that the reaction over time is only slowly rising, then increase it, until the controller regulates to the setpoint in a reasonable amount of time.
- For kd, keep this number to 0 until kp and ki are set. Now, you can use the kd to prevent the regulator from overshooting. Only increase in small steps.

The PID controller code is shared with the [PID thermostat][pid_thermostat]. As an output for the controller, the [Slow PWM][slow_pwm] number can be used.

**This integration will set up the following platforms.**

Platform | Description
-- | --
`number` | This platform can be used to control a number entity output to regulate a sensor value to a specific setpoint. The value of the controlker entity is the setpoint. As a sensor, any numerical sensor entity can be used. If two sensors are configured, the PID controller will act as a differential controller, using the difference between the two sensor values as input signal.


## Installation

### HACS (Preferred)
1. [Add](http://homeassistant.local:8123/hacs/integrations) the custom integration repository: https://github.com/domectrl/ha-pid_controller
2. Select `PID Controller` in the Integration tab and click `download`
3. Restart Home Assistant
4. Done!

### Manual
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `pid_controller`.
1. Download _all_ the files from the `custom_components/pid_controller/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant

## Configuration via user interface:
* In the user interface go to "Configuration" -> "Integrations" click "+" and search for "PID Controller"
* For a description of the configuration parameters, see [Configuration parameters](#configuration-parameters)

## YAML Configuration

Alternatlively, this integration can be configured and set up manually via YAML
instead. To enable the Integration sensor in your installation, add the
following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
number:
  - platform: pid_controller
    name: PID regulator for heat collector
    input1: sensor.water_temperature
    output: number.pwm_pump
```

### Configuration parameters
- name: Name of the PID controller.
  > required: true | type: string
- output: `entity_id` for the output value. Must be a number device. The output will be limited to the minimum and maximum value of this number.
  > required: true | type: string
- input1: `entity_id` for input sensor. Must be a numerical sensor.
  > required: true | type: string
- input2: Optional secondary input sensor. If selected, the controller will work in differential mode.
  > required: false default: `(left empty)`| type: string
- kp: Proportional gain factor, directly gaining the error to compensate the fault (Kp).
  > required: false | default: 1.0 | type: float
- ki: Integration factor, reducing the offset fault over time (Ki).
  > required: false | default: 0.1 | type: float
- kd: Differential factor, damping the overshoot (Kd).
  > required: false | default: 0.0 | type: float
- direction: Regulation direction. When 'direct', the output will increase to decrease fault. When 'reverse', the output will decrease to decrease fault.
  > required: false | default: direct | type: string `('direct' or 'reverse')`
- minimum: Minimal value of the pid_controller number setpoint.
  > required: false | default: 0 | type: float
- maximum: Maximal value of the pid_controller number setpoint.
  > required: false | default: 100 | type: float
- cycle_time: Cycle time for the controller loop.
  > required: false | default: 00:30:00 | type: time_period
- step: Step value. Smallest value `0.001`.
  > required: false | type: float | default: 1
- mode: Control how the number should be displayed in the UI. Can be set to `box` or `slider` to force a display mode.
  > required: false | type: string | default: '"auto"'
- unique_id: Unique id to be able to configure the entity in the UI.
  > required: false | type: string

### Full configuration example

```yaml
number:
  - platform: pid_controller
    name: PID regulator for heat collector
    input1: sensor.water_temperature_in
    input2: sensor.water_temperature_in
    output: number.pwm_pump
    kp: 2.0
    ki: 0.5
    kd: 0.01
    direction: reverse
    minimum: 10
    maximum: 200
    cycle_time:  {'hours':0, 'minutes':01, 'seconds': 00}
    step: 3
    mode: "auto"
    unique_id: "MyUniqueID_1234"
```

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/domectrl/ha-pid_controller.svg?style=for-the-badge
[commits]: https://github.com/domectrl/ha-pid_controller/commits/main
[hacs]: https://hacs.xyz/
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/domectrl/ha-pid_controller.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-domectrl-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/domectrl/ha-pid_controller.svg?style=for-the-badge
[releases]: https://github.com/domectrl/ha-pid_controller/releases
[slow_pwm]: https://github.com/domectrl/ha-slow_pwm
[pid_thermostat]: https://github.com/domectrl/ha_pid_thermostat
