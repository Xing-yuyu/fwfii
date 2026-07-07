#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from fwfii.fc import LED

def _led_op(flight, array, mode, colors, ts, emergency):
    LED(flight, array[0], mode, colors[0], \
                array[1], mode, colors[1], \
                array[2], mode, colors[2], \
                array[3], mode, colors[3], ts, emergency)


def TurnOn(flight, color, ts = 0, emergency = False):
    led_arrays = [0] * 4
    color_arrays = [color] * 4
    _led_op(flight, led_arrays, 0, color_arrays, ts, emergency) 

def TurnOff(flight, ts = 0, emergency = False):
    led_arrays = [0] * 4
    color_arrays = [0] * 4
    _led_op(flight, led_arrays, 1, color_arrays, ts, emergency)     

def Blink(flight, led, color, ts = 0, emergency = False):
    '''
    Make the specified `led` in blinking mode with the specified `color`

    *Parameter*:
    * `flight` - a `Flight` object
    * `led` - the led you want to control, 1 - 12
    * `color` - the RGB color you want to show, 0xFF0000 means red, 0x00FF00 means green and 0x0000FF means blue.
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    led_arrays = [15] * 12
    led_arrays[led - 1] = led - 1
    color_arrays = [0] * 12
    color_arrays[led - 1] = color
    _led_op(flight, led_arrays, 8, color_arrays, ts, emergency)