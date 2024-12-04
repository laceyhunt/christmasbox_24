import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)
BUTTON1_GPIO = 20
BUTTON2_GPIO = 21

# Set the buttons as input
GPIO.setup(BUTTON1_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON2_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to test button presses
try:
    print("Press each button to test which is which")
    while True:
        if GPIO.input(BUTTON1_GPIO) == GPIO.LOW:
            print("Button 1 (GPIO 20) pressed")
            time.sleep(0.5)  # Debounce delay

        if GPIO.input(BUTTON2_GPIO) == GPIO.LOW:
            print("Button 2 (GPIO 21) pressed")
            time.sleep(0.5)  # Debounce delay

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
