import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

SENSOR_PIN=21

GPIO.setup(SENSOR_PIN,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

try:
   while True:
       if GPIO.input(SENSOR_PIN)==GPIO.LOW:
           print("GPIO IS LOW")
           time.sleep(0.2)
       else:
           print("GPIO IS HIGH")
           time.sleep(0.2)
except KeyboardInterrupt:
   print("EXIT")

finally:
    GPIO.cleanup()
