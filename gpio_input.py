import time
import csv
import random
#from pydub import AudioSegment
#from pydub.playback import play
#from pydub.playback import _play_with_simpleaudio
#from io import BytesIO
import sys
import re
import platform


#SENSOR_GPIO=21
SENSOR_GPIO=16
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

GPIO.setmode(GPIO.BCM)
for gpio in KEY_TO_GPIO.values():
    GPIO.setup(gpio, GPIO.OUT)
    GPIO.output(gpio, 1)  # Set default to 1
# Set up the GPIO for input from the motion sensor.  Motion Sensor output is active high
#GPIO.setup(SENSOR_GPIO,GPIO.IN, pull_up_down=GPIO.PUD_OFF)
GPIO.setup(SENSOR_GPIO,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(SENSOR_GPIO,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(SENSOR_GPIO,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)
   

# Initialization

# Create fonts for text

# Define screen size, and set it
#WIDTH, HEIGHT = 860, 540 

# Create the game title bar
# Set up the clock

# Load assets (sounds and images)
bg_sound=["","","","","","","","","","",""]

existing_key_array={}
try:
    if len(sys.argv) > 1:
        input_file=open(sys.argv[1])
        beat_list=list(input_file)
        input_file.close()
        keys=[]
        for i in beat_list:
            index=re.split(",",i.rstrip())[0]
            keys=list(re.split(",",i.rstrip())[1:])
            existing_key_array[eval(index)]=keys
except:
    print("Could not open file: %s" % sys.argv[1])

key=""

running = True
frame_record={}
while(key!="q" and running):
   # Wait for motion
   time.sleep(0.1)
   this_input=GPIO.input(SENSOR_GPIO)
   if this_input==GPIO.LOW:
       print("0",end="")
   else:
       print("1",end="")
   sys.stdout.flush()

GPIO.cleanup()
