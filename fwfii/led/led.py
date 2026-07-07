#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from fwfii.fc import LED

def _led_op(flight, array, mode, colors, ts, emergency):
    LED(flight, array[0], mode, colors[0], \
                array[1], mode, colors[1], \
                array[2], mode, colors[2], \
                array[3], mode, colors[3], ts, emergency)

    LED(flight, array[4], mode, colors[4], \
                array[5], mode, colors[5], \
                array[6], mode, colors[6], \
                array[7], mode, colors[7], ts, emergency)

    LED(flight, array[8], mode, colors[8], \
                array[9], mode, colors[9], \
                array[10], mode, colors[10], \
                array[11], mode, colors[11], ts, emergency)


def TurnOnSingle(flight, led, color, ts = 0, emergency = False):
    '''
    Turn on the specified `led` with the specified `color`, only available in `F400`

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
    _led_op(flight, led_arrays, 0, color_arrays, ts, emergency) 

def TurnOffSingle(flight, led, ts = 0, emergency = False):
    '''
    Turn off the specified `led`, only available in `F400`

    *Parameter*:
    * `flight` - a `Flight` object
    * `led` - the led you want to control, 1 - 12
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    led_arrays = [15] * 12
    led_arrays[led - 1] = led - 1
    color_arrays = [0] * 12
    _led_op(flight, led_arrays, 1, color_arrays, ts, emergency)     

def TurnOnMulti(flight, leds, colors, ts = 0, emergency = False):
    '''
    Turn on the led list with the color list, only available in `F400`

    *Parameter*:
    * `flight` - a `Flight` object
    * `leds` - a list of led, [1, 2, 3] for example
    * `colors` - a list of color. [0xFF0000, 0x00FF00, 0x0000FF] for example, 
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    led_arrays = [15] * 12
    color_arrays = [0] * 12
    for idx, led in enumerate(leds):
        led_arrays[led - 1] = led - 1
        color_arrays[led - 1] = colors[idx]
    _led_op(flight, led_arrays, 2, color_arrays, ts, emergency) 

def TurnOffMulti(flight, leds, ts = 0, emergency = False):
    '''
    Turn off a group of led, only available in `F400`

    *Parameter*:
    * `flight` - a `Flight` object
    * `leds` - a list of led, [1, 2, 3] for example
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    led_arrays = [15] * 12
    color_arrays = [0] * 12
    for led in leds:
        led_arrays[led - 1] = led - 1
    _led_op(flight, led_arrays, 3, color_arrays, ts, emergency)               
        

def TurnOnAll(flight, colors, ts = 0, emergency = False):
    '''
    Turn on all of the leds with the specified color list

    *Parameter*:
    * `flight` - a `Flight` object
    * `colors` - a list of color. [0xFF0000, 0x00FF00, 0x0000FF, ...] for example, fill the list with 12 colors 
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    led_arrays = range(0, 12)
    color_arrays = colors
    _led_op(flight, led_arrays, 4, color_arrays, ts, emergency)   

def TurnOffAll(flight, ts = 0, emergency = False):
    '''
    Turn off all the leds

    *Parameter*:
    * `flight` - a `Flight` object
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    led_arrays = range(0, 12)
    color_arrays = [0] * 12
    _led_op(flight, led_arrays, 5, color_arrays, ts, emergency)   

def BlinkSingle(flight, led, color, ts = 0, emergency = False):
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

def BlinkFastAll(flight, colors, ts = 0, emergency = False):
    '''
    Make all of the leds in fast blinking mode with a color list `colors`

    *Parameter*:
    * `flight` - a `Flight` object
    * `colors` - a list of color. [0xFF0000, 0x00FF00, 0x0000FF, ...] for example, fill the list with 12 colors 
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    led_arrays = range(0, 12)
    color_arrays = colors
    _led_op(flight, led_arrays, 9, color_arrays, ts, emergency)

def BlinkSlowAll(flight, colors, ts = 0, emergency = False):
    '''
    Make all of the leds in slowly blinking mode with a color list `colors`

    *Parameter*:
    * `flight` - a `Flight` object
    * `colors` - a list of color. [0xFF0000, 0x00FF00, 0x0000FF, ...] for example, fill the list with 12 colors 
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    led_arrays = range(0, 12)
    color_arrays = colors
    _led_op(flight, led_arrays, 10, color_arrays, ts, emergency)    

def BlinkAll(flight, colors, ts = 0, emergency = False):
    '''
    Make all the leds in blinking mode with a color list `colors`

    *Parameter*:
    * `flight` - a `Flight` object
    * `colors` - a list of color. [0xFF0000, 0x00FF00, 0x0000FF, ...] for example, fill the list with 12 colors 
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    led_arrays = range(0, 12)
    color_arrays = colors
    _led_op(flight, led_arrays, 11, color_arrays, ts, emergency)    

def Breath(flight, leds, colors, ts = 0, emergency = False):
    '''
    Make the specified led list `leds` in breath mode with a color list `colors`

    *Parameter*:
    * `flight` - a `Flight` object
    * `leds` - a list of led, [1, 2, 3] for example
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True
    '''
    led_arrays = [15] * 12
    color_arrays = [0] * 12
    for idx, led in enumerate(leds):
        led_arrays[led - 1] = led - 1
        color_arrays[led - 1] = colors[idx]
    _led_op(flight, led_arrays, 12, color_arrays, ts, emergency)  

def HorseRace(flight, colors, ts = 0, emergency = False):
    '''
    Make all of leds in a horse race mode with the specified color list `colors`

    *Parameter*:
    * `flight` - a `Flight` object
    * `colors` - a list of color. [0xFF0000, 0x00FF00, 0x0000FF, ...] for example, fill the list with 12 colors 
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    led_arrays = range(0, 12)
    color_arrays = colors
    _led_op(flight, led_arrays, 25, color_arrays, ts, emergency)