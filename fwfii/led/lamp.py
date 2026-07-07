#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from fwfii.fc import LED, DUTY

def _lamp_op(flight, array, mode, colors, A, B, ts, emergency):
    LED(flight, array[0], mode, colors[0], \
                array[0], mode, colors[0], \
                array[0], mode, colors[0], \
                array[0], mode, colors[0], ts, emergency)

    DUTY(flight, A, B, ts, emergency)

    LED(flight, array[1], mode, colors[1], \
                array[2], mode, colors[2], \
                array[3], mode, colors[3], \
                array[4], mode, colors[4], ts, emergency)

def _adjust_brightness(color, brightness):

    return (int(((color & 0xFF0000) >> 16) * brightness) << 16) | \
           (int(((color & 0x00FF00) >> 8) * brightness) << 8) | \
           (int(((color & 0x0000FF)) * brightness))

def AllOn(flight, color, brightness = 1, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [_adjust_brightness(color, brightness)] * 5
    _lamp_op(flight, led_arrays, 0b00111111, color_arrays, 0, 0, ts, emergency)

def AllOff(flight, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [0] * 5
    _lamp_op(flight, led_arrays, 0b00111000, color_arrays, 0, 0, ts, emergency)

def AllBlink(flight, color, A, B, brightness = 1, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [_adjust_brightness(color, brightness)] * 5
    _lamp_op(flight, led_arrays, 0b00110001, color_arrays, int(A / 100), int(B / 100), ts, emergency)

def AllBreath(flight, color, A, B, brightness = 1, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [_adjust_brightness(color, brightness)] * 5
    _lamp_op(flight, led_arrays, 0b00110010, color_arrays, int(A / 100), int(B / 100), ts, emergency)

def BodyOn(flight, color, brightness = 1, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [_adjust_brightness(color, brightness)] * 5
    _lamp_op(flight, led_arrays, 0b01011111, color_arrays, 0, 0, ts, emergency)

def BodyOff(flight, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [0] * 5
    _lamp_op(flight, led_arrays, 0b01011000, color_arrays, 0, 0, ts, emergency)  

def BodyBlink(flight, color, A, B, brightness = 1, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [_adjust_brightness(color, brightness)] * 5
    _lamp_op(flight, led_arrays, 0b01010001, color_arrays, int(A / 100), int(B / 100), ts, emergency)

def BodyBreath(flight, color, A, B, brightness = 1, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [_adjust_brightness(color, brightness)] * 5
    _lamp_op(flight, led_arrays, 0b01010010, color_arrays, int(A / 100), int(B / 100), ts, emergency)

def MotorOn(flight, id, color, brightness = 1, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [_adjust_brightness(color, brightness)] * 5  
    if id == 0:
        mode = 0b11111111
    elif id == 3:
        mode = 0b00011111
    elif id == 4:
        mode = 0b00101111
    elif id == 1:
        mode = 0b01001111
    elif id == 2:
        mode = 0b10001111
    else:
        mode = 0
    _lamp_op(flight, led_arrays, mode, color_arrays, 0, 0, ts, emergency)

def MotorOff(flight, id, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [0] * 5  
    if id == 0:
        mode = 0b11111000
    elif id == 3:
        mode = 0b00011000
    elif id == 4:
        mode = 0b00101000
    elif id == 1:
        mode = 0b01001000
    elif id == 2:
        mode = 0b10001000
    else:
        mode = 0
    _lamp_op(flight, led_arrays, mode, color_arrays, 0, 0, ts, emergency)

def MotorBlink(flight, id, color, A, B, brightness = 1, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [_adjust_brightness(color, brightness)] * 5
    if id == 0:
        mode = 0b11110001
    elif id == 3:
        mode = 0b00010001
    elif id == 4:
        mode = 0b00100001
    elif id == 1:
        mode = 0b01000001
    elif id == 2:
        mode = 0b10000001
    else:
        mode = 0
    _lamp_op(flight, led_arrays, mode, color_arrays, int(A / 100), int(B / 100), ts, emergency)

def MotorBreath(flight, id, color, A, B, brightness = 1, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [_adjust_brightness(color, brightness)] * 5
    if id == 0:
        mode = 0b11110010
    elif id == 3:
        mode = 0b00010010
    elif id == 4:
        mode = 0b00100010
    elif id == 1:
        mode = 0b01000010
    elif id == 2:
        mode = 0b10000010
    else:
        mode = 0
    _lamp_op(flight, led_arrays, mode, color_arrays, int(A / 100), int(B / 100), ts, emergency)    

def MotorHorse(flight, colors, clockwise, duration, brightness = 1, ts = 0, emergency = False):
    led_arrays = range(0, 5)
    color_arrays = [0] * 5
    color_arrays[1] = _adjust_brightness(colors[2], brightness)
    color_arrays[2] = _adjust_brightness(colors[3], brightness)
    color_arrays[3] = _adjust_brightness(colors[1], brightness)
    color_arrays[4] = _adjust_brightness(colors[0], brightness)

    if clockwise:
        mode = 0b11110011
    else:
        mode = 0b11110111
    
    _lamp_op(flight, led_arrays, mode, color_arrays, int(duration / 100), 0, ts, emergency)

