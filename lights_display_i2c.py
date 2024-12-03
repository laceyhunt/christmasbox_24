import smbus
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

#I2c Setup for the dimmer
bus=smbus.SMBus(1)
DEVICE_ADDRESS=0x27
CHANNEL_BASE=0x80
ATTENUATION_LEVEL=0
message=[CHANNEL_BASE,ATTENUATION_LEVEL,CHANNEL_BASE+1,ATTENUATION_LEVEL,CHANNEL_BASE+2,ATTENUATION_LEVEL,CHANNEL_BASE+3,ATTENUATION_LEVEL]
try:
    bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
except:
    bad_write=1
    print("I2C ERROR")

SENSOR_GPIO=16
this_plat=platform.uname()[4]
if this_plat=="armv7l":
    import RPi.GPIO as GPIO

# Map keys to GPIO pins
KEY_TO_GPIO = {
    "a": 0,   # CH0
    "s": 1,   # CH1
    "d": 2,   # CH2
    "f": 3,   # CH3
}
CH_TO_ATT = {
    0: 0,   # CH0
    1: 0,   # CH1
    2: 0,   # CH2
    3: 0,   # CH3
}

if this_plat=="armv7l":
   # Setup GPIO
   GPIO.setmode(GPIO.BCM)
   # Set up the GPIO for input from the motion sensor.  Motion Sensor output is active high
   GPIO.setup(SENSOR_GPIO,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
   GPIO.setwarnings(False)
   

# Initialization
pygame.mixer.pre_init(32000,-16,2,15000000)
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Create fonts for text
font=pygame.font.SysFont(None,24)
go_font=pygame.font.SysFont(None,200)
font_100=pygame.font.SysFont(None,100)
intro_font=pygame.font.SysFont(None,100)

# Define screen size, and set it
WIDTH, HEIGHT = 860, 540 
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Create the game title bar
pygame.display.set_caption('Christmas Lights')
# Set up the clock
clock = pygame.time.Clock()

# Load assets (sounds and images)
bg_sound=["","","","","","","","","","",""]
#bg_sound[0]=pygame.mixer.Sound('sounds/deck_the_halls_manheim_steamroller.wav')
#pygame.mixer.music.load('sounds/EyeOfTheTiger.wav')
pygame.mixer.music.load('sounds/ChristmasTrainFinal1.wav')

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
state=0
running = True
frame_record={}
while(key!="q" and running):
   #levels_loop
   screen.fill((0, 0, 200))
   #intro_text=intro_font.render("Level %d" %current_level, True, (255, 255, 255))
   #screen.blit(intro_text, (960-intro_text.get_width()/2, 540-intro_text.get_height()/2))
   #pygame.display.flip()
   #time.sleep(3)
   # Main Loop
   #bg_sound[0].play()
   #bg_sound[0].stop()
   #pygame.mixer.music.play()
   #pytame.mixer.music.stop()
   intro_text=intro_font.render("Ready", True, (255, 255, 255))
   screen.blit(intro_text, ((960/2)-intro_text.get_width()/2, (540/2)-intro_text.get_height()/2))
   pygame.display.flip()
   time.sleep(1)
   screen.fill((0, 0, 200))
   intro_text=intro_font.render("WAIT FOR MOTION", True, (255, 255, 255))
   screen.blit(intro_text, ((960/2)-intro_text.get_width()/2, (540/2)-intro_text.get_height()/2))
   pygame.display.flip()
   # Wait for motion
   while GPIO.input(SENSOR_GPIO)==GPIO.HIGH:
      time.sleep(0.2)
   screen.fill((0, 0, 200))
   intro_text=intro_font.render("Go!!", True, (255, 255, 255))
   screen.blit(intro_text, ((960/2)-intro_text.get_width()/2, (540/2)-intro_text.get_height()/2))
   pygame.display.flip()
   time.sleep(0.1)
   #bg_sound[0].play()
   pygame.mixer.music.play()
   key_delay=0
   key_array=[]
   loop_count=0
   tgt_framerate=30
   framerate=30
   accum=0
   cumulative_offset=0.0
   dt_array=[]
   desired_duration= 1000.0/tgt_framerate
   desired_durations=[desired_duration for _ in range(15)]
   while (key!="q" and running):
       actual_frame_duration=clock.tick()
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               running = False
           elif event.type == pygame.KEYDOWN:
               this_key=chr(event.key)
               key_array.append(this_key) 
               key=this_key
               #if event.unicode=="p" and game_over==0 and you_won==0:
               #    paused=not paused
               #    pause_sound.play()
               #    if paused==True:
               #       bg_sound[current_level-1].stop()
               #    else:
               #       bg_sound[current_level-1].play(loops=-1)
               #else:
               #    answer_input += event.unicode
           elif event.type == pygame.KEYUP:
               key_array.remove(chr(event.key))
   
       screen.fill((0, 0, 200))
       key_text=""
       for this_key in key_array:
           if key_text!="":
              key_text=key_text+","+this_key
           else:
              key_text=this_key
       beat_keys=[]
       if len(existing_key_array.keys()) > loop_count:
           if loop_count-key_delay >=0: 
              beat_keys=existing_key_array[loop_count-key_delay]
       for this_key in beat_keys:
           if this_key not in key_array:
              if key_text!="":
                 key_text=key_text+","+this_key
              else:
                 key_text=this_key
       if GPIO.input(SENSOR_GPIO)==GPIO.HIGH:
           state=state+1
           if state>3 or state < 1:
               state=1
           pygame.mixer.music.fadeout(2000)
           if state==1:
              pygame.mixer.music.load('sounds/ChristmasTrainFinal1.wav')
           if state==2:
              pygame.mixer.music.load('sounds/ChristmasTrainFinal2.wav')
           if state==3:
              pygame.mixer.music.load('sounds/ChristmasTrainFinal3.wav')
           pygame.mixer.music.play()
           # QUEUE Next song here, but dont play until another LOW is detected (ADD LATER)
       # Assert GPIO's according to what keys are pressed
       key_list=key_text.split(",")
       if this_plat=="armv7l":
          for this_key in KEY_TO_GPIO.keys():
              channel=KEY_TO_GPIO.get(this_key)
              if this_key in key_list:
                 CH_TO_ATT[channel]=100
              else:
                 CH_TO_ATT[channel]=0
              message=[CHANNEL_BASE,CH_TO_ATT[0],CHANNEL_BASE+1,CH_TO_ATT[1],CHANNEL_BASE+2,CH_TO_ATT[2],CHANNEL_BASE+3,CH_TO_ATT[3]]
              try:
                 bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
              except:
                 bad_write=1
                 print("I2C ERROR")
       key_text_gen=intro_font.render(key_text, True, (255, 255, 255))
       screen.blit(key_text_gen, ((960/2)-key_text_gen.get_width()/2, (540/2)-key_text_gen.get_height()/2))
       count_gen=font.render(str(loop_count), True, (255, 255, 255))
       screen.blit(count_gen, ((960/2)-count_gen.get_width()/2, 50-count_gen.get_height()/2))
       pygame.display.flip()
       frame_record[loop_count]=key_text
       frame_offset=desired_duration-actual_frame_duration
       cumulative_offset+= frame_offset
       adjusted_frame_duration=max(1,desired_duration+cumulative_offset)
       adj_framerate= 1000.0/adjusted_frame_duration
       loop_count=loop_count+1
       frame_duration=clock.tick(framerate)
       dt_array.append(frame_duration)
       desired_durations.pop(0)
       desired_durations.append(frame_duration)
       avg_frame_duration=sum(desired_durations)/len(desired_durations)
       avg_fps=1000.0 / avg_frame_duration
       fps_error=tgt_framerate-avg_fps
       framerate=tgt_framerate+fps_error
       print("Current fps: %f, avg fps: %f, %d" % (1000/frame_duration,avg_fps,state))


out_file=open("key_save","w")
for i in frame_record.keys():
    print("%d,%s" % (i,frame_record[i]),file=out_file)
out_file.close()
this_sum=0
for i in dt_array:
    this_sum=this_sum+i
this_sum=this_sum/len(dt_array)
print("Avg Framerate: %f:" % (1/(this_sum/1000)))

GPIO.cleanup()
pygame.quit()
