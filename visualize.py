"""
 Blinks an LED on digital pin 13
 in 1 second intervals
"""

from Arduino import Arduino
import time

import pyaudio
import os
import struct
import numpy as np
from scipy.fftpack import fft

from statistics import mean

GREEN = 4
RED = 7
BLUE = 8

board = Arduino("9600", port="COM3") # plugged in via USB, serial com at rate 115200
board.pinMode(GREEN, "OUTPUT")
board.pinMode(RED, "OUTPUT")
board.pinMode(BLUE, "OUTPUT")

board.digitalWrite(RED, "LOW")
board.digitalWrite(BLUE, "LOW")
board.digitalWrite(GREEN, "LOW")


# constants
CHUNK = 1024 * 2             # samples per frame
FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
CHANNELS = 1                 # single channel for microphone
RATE = 44100                 # samples per second

# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

print('stream started')

rs = [10 for i in range(100)]
bs = [10 for i in range(100)]
gs = [10 for i in range(100)]

cycle = 0
while True:
    
    # binary data
    data = stream.read(CHUNK)  
    
    # convert data to integers, make np array, then offset it by 127
    data_int = struct.unpack(str(2 * CHUNK) + 'B', data)

    # compute FFT and update line
    yf = np.abs(fft(data_int))

    # compute logs of max in three frequency bands
    b_raw = np.log(np.max(yf[50:250]))
    r_raw = np.log(np.max(yf[250:2000]))
    g_raw = np.log(np.max(yf[2000:]))

    # find b relative to the mean of values for this range
    b = b_raw / mean(bs)
    r = r_raw / mean(rs)
    g = g_raw / mean(gs)

    # establish a range of values early on
    if cycle < 100:
        rs = [r_raw] + rs[:-1]
        bs = [b_raw] + bs[:-1]
        gs = [g_raw] + gs[:-1]

    cycle += 1

    # update lights every four analyses
    if cycle % 4 == 0:
        if r < 1: 
            board.digitalWrite(RED, "LOW")
        else:
            board.digitalWrite(RED, "HIGH")

        if g < 1: 
            board.digitalWrite(GREEN, "LOW")
        else:
            board.digitalWrite(GREEN, "HIGH")

        if b < 1: 
            board.digitalWrite(BLUE, "LOW")
        else:
            board.digitalWrite(BLUE, "HIGH")

