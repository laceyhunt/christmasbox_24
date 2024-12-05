import threading
import http.server
import socketserver
import urllib
import smbus
import time
import pygame
import csv
from io import BytesIO
import sys
import re
import platform
import math

##############################################################################################
## Http Server part
##############################################################################################
# "state_valu" global allows us to be able to communicate from the server to the pygame loop running
state_value = 4
server_running = True

# Custom HTTP request handler
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global state_value

        # Parse query parameters
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        local_state = query_components.get("state", [""])[0]
        
        # Update the state value and prepare response text
        state_value = local_state
        response_text=bytes(str(state_value),'utf-8')
        print("NEW STATE: %d" % (int(state_value)))

        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        # Add CORS headers below
        self.send_header('Access-Control-Allow-Origin', '*') # Allows all origins
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
        self.end_headers()
        self.wfile.write(response_text)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    # Just put this in here in case there is an exception and if there isn't good cleanup maybe we can restart the script without having to reboot.
    allow_reuse_address = True

# Start HTTP server in a separate thread so that it doesn't block the pygame stuff while waiting for http requests.
def start_server():
    global server_running
    with ThreadedTCPServer(("", 8000), CustomHandler) as httpd:
        print("Serving at port", 8000)
        while server_running:
            httpd.handle_request()
        print("Server closed")

# Start the server thread
# server_thread = threading.Thread(target=start_server)
# server_thread.daemon = True
# server_thread.start()

##############################################################################################
## Functions and definitions for light control
##############################################################################################
NUM_VALUES = 50  # Number of values in the dimmer array

# Array for the dimmer
brightness_array=[0,3,7,10,13,14,17,20,23,25,28,30,32,34,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71]

def get_dimmer_value(amplitude, frequency, time, phase):
    # Ensure amplitude is within the range of the dimmer array
    scaled_amplitude = min(amplitude, NUM_VALUES // 2)

    # Calculate the sine wave value with phase offset
    sine_value = math.sin(2 * math.pi * frequency * time + phase)

    # Adjust the sine wave to cover the range defined by the amplitude
    # The sine wave oscillates between -1 and 1, so we adjust it to go from 0 to 2 * scaled_amplitude
    dimmer_value = int((sine_value + 1) / 2 * (2 * scaled_amplitude))

    return dimmer_value


# Define where things are hooked up
SENSOR_GPIO=16
BUTTON1_GPIO=20
BUTTON2_GPIO=21

# check platform, in case we are testing on PC (this is NOT complete)
# this_plat=platform.uname()[4]
# if this_plat=="armv7l":
import RPi.GPIO as GPIO
# Setup GPIO
GPIO.setmode(GPIO.BCM)
# Set up the GPIO for input from the motion sensor.  Motion Sensor output is active high
GPIO.setup(SENSOR_GPIO,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setwarnings(False)
#for the ADC - not currently used
#import ADS1x15
#adc = ADS1x15.ADS1115()
#GAIN = 1

#I2c Setup for the dimmer
bus=smbus.SMBus(1)
# I2C Address for the dimmer
DEVICE_ADDRESS=0x27
# Register base addres for individual dimmer channels
CHANNEL_BASE=0x80

# Write an initial value for the lights to turn everything on
bad_write=0
ATTENUATION_LEVEL=0
message=[CHANNEL_BASE,ATTENUATION_LEVEL,CHANNEL_BASE+1,ATTENUATION_LEVEL,CHANNEL_BASE+2,ATTENUATION_LEVEL,CHANNEL_BASE+3,ATTENUATION_LEVEL]
# Wrap a try except around the I2C write so we dont exit if there is an I2C error.
try:
    bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
except:
    bad_write+=1
    print("I2C ERROR")


##############################################################################################
## PYGAME PART
##############################################################################################
time_elapsed=0
#amplitude = 25  # Half the range of the dimmer array is MAX, or 25 in this case
amplitude = 15  # Half the range of the dimmer array
frequency=0
multiplier=4
# bad_write=0
recording_on=0
fade_in_timer_max=45
fade_in_timer=fade_in_timer_max
try:
   # Start at state 4, where no music is playing, and lights are just doing something or constant on
   last_state=4
   state=4

   # Map action keys to channels / index
   KEY_TO_CH = {
       "a": 0,   # CH0
       "s": 1,   # CH1
       "d": 2,   # CH2
       "f": 3,   # CH3
   }
   # Mode keys to channels / index 
   MODE_KEYS = {
       "q": 0,   # CH0
       "w": 1,   # CH1
       "e": 2,   # CH2
       "r": 3,   # CH3
   }
   MAX_KEYS = {
       "z": 0,   # CH0
       "x": 1,   # CH1
       "c": 2,   # CH2
       "v": 3,   # CH3
   }

      
   # This list is an index into the attentuation array
   ATTENUATION_LIST=[0,0,0,0]
   # MODES:  0=Constant on, dim to mode0_index when asdf pressed
   #         1=sine wave dimmer motion
   if state==4:
      MODE_LIST=[0,0,0,0]
   else:
      MODE_LIST=[1,1,1,1]
   LAST_MODE_PRESS=[0,0,0,0]
   # 
   PRESSED_LIST=[0,0,0,0]
   #
   MAX_LIST=[0,0,0,0]
   #
   CH_PHASE=[0,math.pi/4,2*math.pi/4,3*math.pi/4]
   
   #pygame.mixer.pre_init(32000,-16,2,15000000)
   pygame.init()
   pygame.mixer.init()
   
   # Set up the clock
   clock = pygame.time.Clock()
   
   # Load assets (sounds and images)
   #pygame.mixer.music.load('sounds/EyeOfTheTiger.wav')
   sounds=["" for i in range(3)]
   sounds[0]=pygame.mixer.Sound('sounds/ChristmasTrainFinal1.wav')
   sounds[1]=pygame.mixer.Sound('sounds/ChristmasTrainFinal2.wav')
   sounds[2]=pygame.mixer.Sound('sounds/ChristmasTrainFinal3.wav')
 
   screen = pygame.display.set_mode((100, 200))
   pygame.display.set_caption('Christmas Lights')

   # create a list of dictionaries, one for each state
   existing_key_array=[{} for stuff in range(4)]
   try:
       if len(sys.argv) > 4:
           for file_idx in range(4):
              input_file=open(sys.argv[file_idx+1])
              beat_list=list(input_file)
              input_file.close()
              keys=[]
              for i in beat_list:
                  index=re.split(",",i.rstrip())[0]
                  keys=list(re.split(",",i.rstrip())[1:])
                  existing_key_array[file_idx][eval(index)]=keys
   except:
       print("Could not open file: %s" % sys.argv[1])
   
   key=""
   running = True
   # Allow recording different sets depending on what state we are in
   frame_record=[{} for stuff in range(4)]
   key_max_indexes=[0,0,0,0]
   if len(sys.argv)>4:
       key_max_indexes[0]=len(existing_key_array[0])
       key_max_indexes[1]=len(existing_key_array[1])
       key_max_indexes[2]=len(existing_key_array[2])
       key_max_indexes[3]=len(existing_key_array[3])

   while(key!="p" and running):
      key_delay=0
      key_array=[]
      all_keys=[]
      loop_count=0
      last_o=0
      tgt_framerate=30
      framerate=30
      accum=0
      cumulative_offset=0.0
      dt_array=[]
      desired_duration= 1000.0/tgt_framerate
      desired_durations=[desired_duration for _ in range(15)]
      # Below is if we are using the ADC to control dimming
      #values = [0]*4

      ####################################################################################
      ## Main PYGAME LOOP
      ####################################################################################
      while (key!="p" and running):
          actual_frame_duration=clock.tick()
          screen.fill((0,200,0))
          pygame.display.flip()

          # Check for keys presses
          keyup=""
          for event in pygame.event.get():
              if event.type == pygame.QUIT:
                  running = False
              elif event.type == pygame.KEYDOWN:
                  this_key=chr(event.key)
                  if this_key in ["a","s","d","f","q","w","e","r","z","x","c","v"]:
                     key_array.append(this_key) 
                  all_keys.append(this_key)
                  key=this_key
              elif event.type == pygame.KEYUP:
                  this_key=chr(event.key)
                  if this_key in ["a","s","d","f","q","w","e","r","z","x","c","v"]:
                     key_array.remove(chr(event.key))
                  all_keys.remove(this_key)
          if "o" in all_keys and last_o==0:
              recording_on=1-recording_on
              if recording_on==1:
                  print("******RECORDING ON*********")
              else:
                  print("******RECORDING OFF********")
              last_o=1
          if "o" not in all_keys:
              last_o=0
          key_text=""
          for this_key in key_array:
              if key_text!="":
                 key_text=key_text+","+this_key
              else:
                 key_text=this_key

          # Put the keys together into a string to save
          beat_keys=[]
          if len(existing_key_array[state-1].keys()) > loop_count:
              if loop_count-key_delay >=0: 
                 beat_keys=existing_key_array[state-1][loop_count-key_delay]
          for this_key in beat_keys:
              if this_key not in key_array:
                 if key_text!="":
                    key_text=key_text+","+this_key
                 else:
                    key_text=this_key
          
          # Handle state value changes from the server
          mode_change=0
          if state_value!=None:
             mode_change=1
             fade_in_timer=0
             last_state=state
             #if state_value not in [1,2,3,4]:
             #    state=4
             #else:
             #    state=state_value
             state=int(state_value)
             state_value=None
             if last_state!=4:
                 try:
                     sounds[last_state-1].fadeout(2000)
                 except:
                     print("Could not fade sound")
             if state!=4:
                 try:
                     sounds[state-1].play()
                 except:
                     print("Could not play sound for state: %d" % (state))
             if state==1:
                 MODE_LIST=[1,1,1,1]
                 frequency=1.375
                 multiplier=4
             if state==2:
                 MODE_LIST=[0,0,0,0]
                 frequency=0
             if state==3:
                 MODE_LIST=[1,1,1,1]
                 frequency=0.403
                 multiplier=6
             if state==4:
                 MODE_LIST=[0,0,0,0]
                 frequency=0
             loop_count=0
                   
          # Assert GPIO's according to what keys are pressed
          key_list=key_text.split(",")
          PRESSED_LIST=[0,0,0,0]
          MAX_LIST=[0,0,0,0]
          for this_key in key_list:
              if this_key in KEY_TO_CH:
                 PRESSED_LIST[KEY_TO_CH[this_key]]=1 
              if this_key in MAX_KEYS:
                 MAX_LIST[MAX_KEYS[this_key]]=1 
              if this_key in MODE_KEYS:
                 if LAST_MODE_PRESS[MODE_KEYS[this_key]]==0:
                    MODE_LIST[MODE_KEYS[this_key]]=1-MODE_LIST[MODE_KEYS[this_key]]
                    LAST_MODE_PRESS[MODE_KEYS[this_key]]=1
          for chk1 in range(4):
              if LAST_MODE_PRESS[chk1]==1 and this_key not in MODE_KEYS:
                 LAST_MODE_PRESS[chk1]=0

          # This was for setting the light brighness based on a slider control
          #for ii in range(4):
          #    values[ii] = adc.read_adc(ii, gain=GAIN)
         
          #print("VALUES: ",end="")
          #print(values)
          #for iii in range(4):
          #   index=int(values[iii]/510)
          #   if index>len(brightness_array)-1:
          #      index=len(brightness_array)-1
          #   if index < 0:
          #      index=0
          #   print("INDEX: %d, %d" % (index,iii))
          #   ATTENUATION_LIST[iii]=brightness_array[index]
          #   if ATTENUATION_LIST[iii] > 70:
          #       ATTENUATION_LIST[iii]=70
   
          #message=[CHANNEL_BASE,ATTENUATION_LIST[0],CHANNEL_BASE+1,ATTENUATION_LIST[1],CHANNEL_BASE+2,ATTENUATION_LIST[2],CHANNEL_BASE+3,ATTENUATION_LIST[3]]
          #print(message)
          #try:
          #   bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
          #except:
          #   bad_write=1
          #   print("I2C ERROR")
 
          amplitude_fade=int((fade_in_timer/fade_in_timer_max)*amplitude)
          if this_plat=="armv7l":
             for channel in range(4):
                if MODE_LIST[channel]==0:
                   ATTENUATION_LIST[channel]=0
                   if PRESSED_LIST[channel]==1:
                      ATTENUATION_LIST[channel]=brightness_array[30]
                   if ATTENUATION_LIST[channel]>70:
                      ATTENUATION_LIST[channel]=100
                else:
                   # if the mode is not 0, then change the "frequency" of the sinusoid based on a button press
                   if PRESSED_LIST[channel]==1:
                      dim_idx=get_dimmer_value(amplitude_fade,frequency*multiplier,time_elapsed,CH_PHASE[channel])
                      ATTENUATION_LIST[channel]=brightness_array[dim_idx]
                      if dim_idx> len(brightness_array)-1:
                          print("DIM IDX OVER RANGE: %d" % (dim_idx))
                          dim_idx=len(brightness_array)-1
                      if dim_idx< 0:
                          dim_idx=0
                   else:
                      dim_idx=get_dimmer_value(amplitude_fade,frequency,time_elapsed,CH_PHASE[channel])
                      if dim_idx> len(brightness_array)-1:
                          print("DIM IDX OVER RANGE: %d" % (dim_idx))
                          dim_idx=len(brightness_array)-1
                      if dim_idx< 0:
                          dim_idx=0
                      ATTENUATION_LIST[channel]=brightness_array[dim_idx]
                   if ATTENUATION_LIST[channel]>70:
                      ATTENUATION_LIST[channel]=100
                # If there is a channel set in the MAX_LIST, set attenuation to 0 regardless of other settings
                if MAX_LIST[channel]==1 or mode_change==1:
                    ATTENUATION_LIST[channel]=0
          message=[CHANNEL_BASE,ATTENUATION_LIST[0],CHANNEL_BASE+1,ATTENUATION_LIST[1],CHANNEL_BASE+2,ATTENUATION_LIST[2],CHANNEL_BASE+3,ATTENUATION_LIST[3]]
          try:
             bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
          except:
             bad_write+=1
             print("I2C ERROR")
          if recording_on==1: 
             frame_record[state-1][loop_count]=key_text
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
          print("Current fps: %f, avg fps: %f, %d" % (1000/frame_duration,avg_fps,state),end="")
          print(MODE_LIST,end="")
          print(PRESSED_LIST,end="")
          print(ATTENUATION_LIST)
          time_elapsed+=1/tgt_framerate
          fade_in_timer+=1
          if fade_in_timer> fade_in_timer_max:
              fade_in_timer=fade_in_timer_max
  
   for stuff in range(4):
      out_file=open("key_save."+str(stuff+1),"w")
      for i in frame_record[stuff].keys():
          print("%d,%s" % (i,frame_record[stuff][i]),file=out_file)
      out_file.close()
   this_sum=0
   for i in dt_array:
       this_sum=this_sum+i
   this_sum=this_sum/len(dt_array)
   print("Avg Framerate: %f:" % (1/(this_sum/1000)))
   
   GPIO.cleanup()
   pygame.quit()

except KeyboardInterrupt:
    print("Pygame loop interrupted")
finally:
    print("Cleaning up...")
    print("Total Bad Writes: "+str(bad_write))
    # Signal the server thread to stop
    server_running = False
    # Join the server thread here so we can exit it with another CTRL-C
    server_thread.join()
