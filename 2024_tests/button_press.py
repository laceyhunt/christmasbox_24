import RPi.GPIO as GPIO
import time

# Pin setup
BUTTON_GPIO = 20  # Button pin
LIGHT_GPIO = 21   # Light pin

'''
blue to 3.3v
green to gpio 21
brown to ground
orange to gpio 20
'''

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button as input with pull-up
GPIO.setup(LIGHT_GPIO, GPIO.OUT)  # Light as output

try:
    print("Press the button to toggle the light...")
    while True:
        button_state = GPIO.input(BUTTON_GPIO)
        if button_state == GPIO.LOW:  # Button is pressed (low)
            GPIO.output(LIGHT_GPIO, GPIO.HIGH)  # Turn the light off
            time.sleep(2)
        else:
            GPIO.output(LIGHT_GPIO, GPIO.LOW)  # Turn the light on
        time.sleep(0.1)  # Add a small delay to debounce
except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    GPIO.cleanup()  # Clean up GPIO settings