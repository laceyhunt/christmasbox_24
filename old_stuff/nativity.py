# 
#   nativity.py
#       handles all GPIO (light and audio) stuff for nativity
#   Lacey Hunt
#   2023
#
#   Lights and Audio are run in their own respective threads, initialized in this file
# 
#   if state is 2 then initialize Nativity lights and audio
#   else standby
# 

import RPi.GPIO as GPIO
import pygame
import time
import threading
import os
import smbus
import pygame


# event to trigger proper stop of nativity lights and audio
stop_event = threading.Event()

# threads for Nativity lights and audio
audio_thread = None
lights_thread = None

# audio to play with lights
audio_file = os.path.join('..','audio','Christmas_Village_Station_2_AUDIO.wav')
lightsOff=True

# set up I2C
#I2c Setup for the dimmer
bus=smbus.SMBus(1)
bad_write=0
# I2C Address for the dimmer
RELAY_ADDRESS=0x27
# Register base addres for individual dimmer channels
CHANNEL_BASE=0x80

# Write an initial value for the lights to turn everything on
ATTENUATION_LEVEL=0
##############################################################################################
## FUnctions and definitions for light control
##############################################################################################


# Set up the I2C bus
def turn_on_relay(channel):
    bus.write_byte(RELAY_ADDRESS, 0x01 << channel)

def turn_off_relay(channel):
    bus.write_byte(RELAY_ADDRESS, 0x00)

def set_light_attenuation(channel, value):
    # Modify this function based on how your relay board adjusts attenuation
    bus.write_byte(RELAY_ADDRESS, value)
    message=[CHANNEL_BASE,ATTENUATION_LEVEL,CHANNEL_BASE+1,ATTENUATION_LEVEL,CHANNEL_BASE+2,ATTENUATION_LEVEL,CHANNEL_BASE+3,ATTENUATION_LEVEL]
    # Wrap a try except around the I2C write so we dont exit if there is an I2C error.
    try:
        bus.write_i2c_block_data(RELAY_ADDRESS,0,message)
    except:
        bad_write+=1
        print("I2C ERROR")



# Set up GPIO
GPIO.setmode(GPIO.BCM)
RELAY_PINS = [17, 18, 27, 22, 23, 24, 25, 4]
for pin in RELAY_PINS:
    GPIO.setup(pin, GPIO.OUT)

# 
# lights_off()->None
#   set all GPIO pins in RELAY_PINS to off
#
def lights_off():
    global lightsOff
    for pin in RELAY_PINS:
        GPIO.output(pin, GPIO.HIGH)
    lightsOff=True
lights_off()

# 
# lights_on()->None
#   set all GPIO pins in RELAY_PINS to on
#
def lights_on():
    global lightsOff
    for pin in RELAY_PINS:
        GPIO.output(pin, GPIO.LOW)
    lightsOff=False

# 
# play_audio(string)->None
#   initialzes mixer and plays audio while stop_event is not set
# 
def play_audio(file_path):

    # start mixer
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # play while audio is still going and stop_event is not set
    while pygame.mixer.music.get_busy() and not stop_event.is_set():
        pygame.time.Clock().tick(30)

    # quit
    pygame.mixer.quit()
    print("Nativity Sound stopped.")

# 
# nativity_lights()->None
#   control nativity lights while stop_event is not set
#   
def nativity_lights():
    global lightsOff
    # turn lights off if not off already
    if lightsOff == False:
        lights_off()
    # light control loop    
    while not stop_event.is_set():
        lightsOff=False
        print("star")
        # star
        GPIO.output(RELAY_PINS[7], GPIO.LOW)
        if stop_event.is_set():
                break
        time.sleep(27.95)

        print("donkey")
        # donkey
        GPIO.output(RELAY_PINS[6], GPIO.LOW)
        if stop_event.is_set():
                break
        time.sleep(11.12)

        print("camel")
        # camel
        GPIO.output(RELAY_PINS[5], GPIO.LOW)
        if stop_event.is_set():
                break
        time.sleep(4.66)

        print("lamb")
        # lamb
        GPIO.output(RELAY_PINS[4], GPIO.LOW)
        if stop_event.is_set():
                break
        time.sleep(5.73)

        print("cow")
        # cow
        GPIO.output(RELAY_PINS[3], GPIO.LOW)
        if stop_event.is_set():
                break
        time.sleep(5.5)

        print("wisemen")
        # wisemen
        GPIO.output(RELAY_PINS[2], GPIO.LOW)
        if stop_event.is_set():
                break
        time.sleep(9)

        print("joseph and mary")
        # joseph and mary
        GPIO.output(RELAY_PINS[1], GPIO.LOW)
        GPIO.output(RELAY_PINS[0], GPIO.LOW)
        stop_event.set()
    
    # turn off lights
    print("Nativity Lights Stopped.")
    
    
    
    
    
    
        # ####################################################################################
        # ## Main PYGAME LOOP
        # ####################################################################################
        # while (key!="p" and running):
        #     actual_frame_duration=clock.tick()
            
        #     # Assert GPIO's according to what keys are pressed
        #     key_list=key_text.split(",")
        #     PRESSED_LIST=[0,0,0,0]
        #     MAX_LIST=[0,0,0,0]
        #     for this_key in key_list:
        #         if this_key in KEY_TO_CH:
        #             PRESSED_LIST[KEY_TO_CH[this_key]]=1 
        #         if this_key in MAX_KEYS:
        #             MAX_LIST[MAX_KEYS[this_key]]=1 
        #         if this_key in MODE_KEYS:
        #             if LAST_MODE_PRESS[MODE_KEYS[this_key]]==0:
        #             MODE_LIST[MODE_KEYS[this_key]]=1-MODE_LIST[MODE_KEYS[this_key]]
        #             LAST_MODE_PRESS[MODE_KEYS[this_key]]=1
        #     for chk1 in range(4):
        #         if LAST_MODE_PRESS[chk1]==1 and this_key not in MODE_KEYS:
        #             LAST_MODE_PRESS[chk1]=0            
                    
        #     amplitude_fade=int((fade_in_timer/fade_in_timer_max)*amplitude)
        #     # if this_plat=="armv7l":
        #     for channel in range(4):
        #         if MODE_LIST[channel]==0:
        #             ATTENUATION_LIST[channel]=0
        #             if PRESSED_LIST[channel]==1:
        #                 ATTENUATION_LIST[channel]=brightness_array[30]
        #             if ATTENUATION_LIST[channel]>70:
        #                 ATTENUATION_LIST[channel]=100
        #         else:
        #             # if the mode is not 0, then change the "frequency" of the sinusoid based on a button press
        #             if PRESSED_LIST[channel]==1:
        #                 dim_idx=get_dimmer_value(amplitude_fade,frequency*multiplier,time_elapsed,CH_PHASE[channel])
        #                 ATTENUATION_LIST[channel]=brightness_array[dim_idx]
        #                 if dim_idx> len(brightness_array)-1:
        #                     print("DIM IDX OVER RANGE: %d" % (dim_idx))
        #                     dim_idx=len(brightness_array)-1
        #                 if dim_idx< 0:
        #                     dim_idx=0
        #             else:
        #                 dim_idx=get_dimmer_value(amplitude_fade,frequency,time_elapsed,CH_PHASE[channel])
        #                 if dim_idx> len(brightness_array)-1:
        #                     print("DIM IDX OVER RANGE: %d" % (dim_idx))
        #                     dim_idx=len(brightness_array)-1
        #                 if dim_idx< 0:
        #                     dim_idx=0
        #                 ATTENUATION_LIST[channel]=brightness_array[dim_idx]
        #             if ATTENUATION_LIST[channel]>70:
        #                 ATTENUATION_LIST[channel]=100
        #         # If there is a channel set in the MAX_LIST, set attenuation to 0 regardless of other settings
        #         if MAX_LIST[channel]==1 or mode_change==1:
        #             ATTENUATION_LIST[channel]=0
        #     message=[CHANNEL_BASE,ATTENUATION_LIST[0],CHANNEL_BASE+1,ATTENUATION_LIST[1],CHANNEL_BASE+2,ATTENUATION_LIST[2],CHANNEL_BASE+3,ATTENUATION_LIST[3]]
        #     try:
        #         bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
        #     except:
        #         nativity.bad_write+=1
        #         print("I2C ERROR")      

# 
# start_nativity_threads()->Tuple[Thread, Thread]
#   clear stop_event then initialize then start new light and audio threads
#   
def start_nativity_threads():
    global audio_thread, lights_thread, stop_event

    # clear stop_event so threads can run
    stop_event.clear()

    # initialize and start threads
    audio_thread = threading.Thread(target=play_audio, args=(audio_file,))
    lights_thread = threading.Thread(target=nativity_lights)
    audio_thread.start()
    lights_thread.start()

    return audio_thread,lights_thread
    # return lights_thread


# 
# stop_nativity_threads()->None
#   set stop_event and join threads
#   
def stop_nativity_threads():
    global audio_thread, lights_thread, stop_event

    # stop currently running threads
    stop_event.set()

    # join threads if they exist
    # if audio_thread is not None:
    #     audio_thread.join()
    if lights_thread is not None:
        lights_thread.join()