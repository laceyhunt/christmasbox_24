import time
import pygame
import csv
import random
#from pydub import AudioSegment
#from pydub.playback import play
#from pydub.playback import _play_with_simpleaudio
from io import BytesIO
import sys
import re
import platform


SENSOR_GPIO=21
this_plat=platform.uname()[4]
if this_plat=="armv7l":
    import RPi.GPIO as GPIO

# Map keys to GPIO pins
KEY_TO_GPIO = {
    "a": 5,   # GPIO 5
    "s": 6,   # GPIO 6
    "d": 13,   # GPIO 13
    "f": 17,  # GPIO 17
    "h": 27,  # GPIO 27
    "j": 22,  # GPIO 22
    "k": 10,  # GPIO 10
    "l": 9    # GPIO 9
}

if this_plat=="armv7l":
   # Setup GPIO
   GPIO.setmode(GPIO.BCM)
   for gpio in KEY_TO_GPIO.values():
       GPIO.setup(gpio, GPIO.OUT)
       GPIO.output(gpio, 1)  # Set default to 1
   # Set up the GPIO for input from the motion sensor.  Motion Sensor output is active high
   GPIO.setup(SENSOR_GPIO,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
   GPIO.setwarnings(False)
#GPIO.cleanup()   
