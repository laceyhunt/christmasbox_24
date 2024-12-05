import time
import math
import smbus
import RPi.GPIO as GPIO
import os
import signal
import sys

# Initialize I2C
DEVICE_ADDRESS = 0x27
CHANNEL_BASE = 0x80
bus = smbus.SMBus(1)

# GPIO Setup
BUTTON_GPIO = 17  # Example GPIO pin for the button
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define states
STATE = 0
FRAME_RATE = 30
AUDIO_FILE = os.path.join('sounds', 'audio_file.mp3')  # Replace with your audio file path

def all_lights_on():
   """Turn all lights on."""
   try:
      for channel in range(4):
         bus.write_byte_data(DEVICE_ADDRESS, CHANNEL_BASE + channel, 255)
   except OSError:
      print("Error: I2C write failed for lights ON.")

def all_lights_off():
   """Turn all lights off."""
   try:
      for channel in range(4):
         bus.write_byte_data(DEVICE_ADDRESS, CHANNEL_BASE + channel, 0)
   except OSError:
      print("Error: I2C write failed for lights OFF.")

def update_lights_sine_wave(frame_count, frequency=1.0, amplitude=255):
   """Update lights based on a sine wave."""
   try:
      for channel in range(4):
         brightness = int(amplitude * (0.5 * math.sin(frame_count * frequency + channel) + 0.5))
         bus.write_byte_data(DEVICE_ADDRESS, CHANNEL_BASE + channel, brightness)
   except OSError:
      print("Error: I2C write failed for lights update.")

def play_audio(file_path):
   """Play an audio file using the system's audio player."""
   os.system(f"omxplayer --no-keys {file_path} > /dev/null 2>&1 &")

def stop_audio():
   """Stop audio playback."""
   os.system("pkill omxplayer")

def exit_gracefully(signal_num, frame):
   """Handle cleanup on program exit."""
   print("\nExiting gracefully...")
   all_lights_off()
   stop_audio()
   GPIO.cleanup()
   sys.exit(0)

# Attach signal handler for graceful exit
signal.signal(signal.SIGINT, exit_gracefully)

# Initial State: Turn all lights ON
all_lights_on()

# Main Loop
frame_count = 0
audio_playing = False
try:
   while True:
      if STATE == 0:
         # Wait for button press
         if GPIO.input(BUTTON_GPIO) == GPIO.LOW:  # Button pressed
               print("Button pressed. Switching to State 1.")
               STATE = 1
               time.sleep(0.2)  # Debounce delay

      elif STATE == 1:
         # Start audio playback if not already playing
         if not audio_playing:
               print("Starting audio playback.")
               play_audio(AUDIO_FILE)
               audio_playing = True
         
         # Perform main loop behavior
         frame_count += 1
         update_lights_sine_wave(frame_count, frequency=0.1)  # Example frequency
         
         # Check for button press to reset
         if GPIO.input(BUTTON_GPIO) == GPIO.LOW:  # Button pressed again
               print("Button pressed. Switching to State 0.")
               all_lights_on()
               STATE = 0
               audio_playing = False  # Reset audio state
               time.sleep(0.2)  # Debounce delay
         
         # Maintain frame rate
         time.sleep(1 / FRAME_RATE)
except KeyboardInterrupt:
   # Fallback in case signal handler doesn't trigger (rare cases)
   exit_gracefully(None, None)
