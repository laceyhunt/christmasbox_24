import wave
import numpy as np
import pyaudio
import pygame
# import threading
import time
import smbus
import RPi.GPIO as GPIO
from pynput import keyboard
import random

# Pin setup
BUTTON_GPIO = 20  # Button pin
LIGHT_GPIO = 21   # Light pin

STOP_EV=0

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button as input with pull-up
GPIO.setup(LIGHT_GPIO, GPIO.OUT)  # Light as output

# index of brightness_array that the non-star values go to when they are on
BRIGHT_VAL=50
DIM_VAL=60
OFF_VAL =99
ON_VAL =0

BRIGHT_IDX=49
DIM_IDX=28
# Set the target duration in seconds
STAR_ON_TIME = 0
CHANNEL_1_B_TIME = 18
CHANNEL_2_B_TIME = 58
CHANNEL_3_B_TIME = 62
DIM_TIME = 101
ALL_DIM_TIME = 110
STOP_TIME = 115
TEST_INTERVAL=2

SLEEP_TIME= 0.5
ITER_TIME = 0.02

# start values   
CURRENT_ATT_VALS = [0, 0, 0, 0]    
# i2c stuff
# Constants
TALKING_LIGHT_CHANNEL=0
# TEST_DURATION=10
DEVICE_ADDRESS = 0x27  # Replace with your I2C device address
CHANNEL_BASE = 0x80       # Adjust if your channels start from a different base
# TEST_DURATION = 10     # Test duration for each channel in seconds
DIMMER_FREQUENCY = 0.2  # Frequency of the sine wave dimming
# Brightness array
brightness_array = [
   0, 3, 7, 10, 13, 14, 17, 20, 23, 25, 28, 30, 32, 34, 36, 37, 38, 39, 40, 41,
   42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
   62, 63, 64, 65, 66, 67, 68, 69, 70, 71
]
NUM_VALUES = len(brightness_array)
AMPLITUDE = len(brightness_array) // 2  # Maximum amplitude for dimmer values
bad_write=0
# I2C bus setup
bus = smbus.SMBus(1)  # Use 0 for older Raspberry Pi models
   
def set_all_channels(test_val):
   set_att_vals(test_val)
   print(f"all to {test_val}")
   reset_message = [
      CHANNEL_BASE, test_val,
      CHANNEL_BASE + 1, test_val,
      CHANNEL_BASE + 2, test_val,
      CHANNEL_BASE + 3, test_val,
      ]
   try:
      bus.write_i2c_block_data(DEVICE_ADDRESS, 0, reset_message)
   except Exception as e:
      print(f"Error resetting channels: {e}")
   #  time.sleep(1)
   
def channel_test(test_val,channel=-1):
   global CURRENT_ATT_VALS
   if(channel==-1):
      # print(f"all to {test_val}")
      reset_message = [
         CHANNEL_BASE, test_val,
         CHANNEL_BASE + 1, test_val,
         CHANNEL_BASE + 2, test_val,
         CHANNEL_BASE + 3, test_val,
      ]
      CURRENT_ATT_VALS=[test_val,test_val,test_val,test_val]
   else:
      v_0=CURRENT_ATT_VALS[0]
      v_1=CURRENT_ATT_VALS[1]
      v_2=CURRENT_ATT_VALS[2]
      v_3=CURRENT_ATT_VALS[3]
      if channel==1:
         v_1=test_val
         CURRENT_ATT_VALS[1]=test_val
      if channel==2:
         v_2=test_val
         CURRENT_ATT_VALS[2]=test_val
      elif channel==3:
         v_3=test_val
         CURRENT_ATT_VALS[3]=test_val
      # print(f"channel {channel} to {test_val}")
      reset_message = [
         CHANNEL_BASE, v_0,
         CHANNEL_BASE + 1, v_1,
         CHANNEL_BASE + 2, v_2,
         CHANNEL_BASE + 3, v_3,
      ]
   try:
      bus.write_i2c_block_data(DEVICE_ADDRESS, 0, reset_message)
   except Exception as e:
      print(f"Error resetting channels {channel}: {e}")
   #  time.sleep(0)
def all_off():
   global CURRENT_ATT_VALS
   try:
      print("turning off...")
      set_att_vals(OFF_VAL)
      for i in range(OFF_VAL):
         channel_test(i)
         time.sleep(ITER_TIME)
      print("all off now...")
      time.sleep(SLEEP_TIME)
      # time.sleep(3)
   except Exception as e:
      print(f"Error in all_off: {e}") 
      
def set_att_vals(value):
   global CURRENT_ATT_VALS
   CURRENT_ATT_VALS[0]=value
   CURRENT_ATT_VALS[1]=value
   CURRENT_ATT_VALS[2]=value
   CURRENT_ATT_VALS[3]=value
   
def two_three_helper(test_val):
   global CURRENT_ATT_VALS
   # print(f"2,3 to {test_val}")
   CURRENT_ATT_VALS[2]=test_val
   CURRENT_ATT_VALS[3]=test_val
   reset_message = [
      CHANNEL_BASE, CURRENT_ATT_VALS[0],
      CHANNEL_BASE + 1, CURRENT_ATT_VALS[1],
      CHANNEL_BASE + 2, test_val,
      CHANNEL_BASE + 3, test_val,
      ]
   try:
      bus.write_i2c_block_data(DEVICE_ADDRESS, 0, reset_message)
   except Exception as e:
      print(f"Error resetting channels: {e}")
def idx_two_three_off():
   try:
      print("turning 2 and 3 off...")
      for i in range(OFF_VAL):
         two_three_helper(i)
         time.sleep(ITER_TIME)
      print("2,3 off now...")
      time.sleep(SLEEP_TIME)
      # time.sleep(3)
   except Exception as e:
      print(f"Error in idx_two_three_off: {e}") 
def one_helper(test_val):
   global CURRENT_ATT_VALS
   # print(f"one to {test_val}")
   CURRENT_ATT_VALS[1]=test_val
   reset_message = [
      CHANNEL_BASE, CURRENT_ATT_VALS[0],
      CHANNEL_BASE + 1, test_val,
      CHANNEL_BASE + 2, CURRENT_ATT_VALS[2],
      CHANNEL_BASE + 3, CURRENT_ATT_VALS[3],
      ]
   try:
      bus.write_i2c_block_data(DEVICE_ADDRESS, 0, reset_message)
   except Exception as e:
      print(f"Error resetting channels: {e}")
def idx_one_off():
   # global CURRENT_ATT_VALS
   # CURRENT_ATT_VALS[1]=71
   try:
      print("turning 1 off...")
      for i in range(OFF_VAL):
         one_helper(i)
         time.sleep(ITER_TIME)
      print("1 off now...")
      time.sleep(SLEEP_TIME)
      # time.sleep(3)
   except Exception as e:
      print(f"Error in one_off: {e}") 
def zero_helper(test_val):
   global CURRENT_ATT_VALS
   # print(f"one to {test_val}")
   CURRENT_ATT_VALS[0]=test_val
   reset_message = [
      CHANNEL_BASE, test_val,
      CHANNEL_BASE + 1, CURRENT_ATT_VALS[1],
      CHANNEL_BASE + 2, CURRENT_ATT_VALS[2],
      CHANNEL_BASE + 3, CURRENT_ATT_VALS[3],
      ]
   try:
      bus.write_i2c_block_data(DEVICE_ADDRESS, 0, reset_message)
   except Exception as e:
      print(f"Error resetting channels: {e}")
def idx_zero_off():
   # global CURRENT_ATT_VALS
   # CURRENT_ATT_VALS[1]=71
   try:
      print("turning 0 off...")
      for i in range(OFF_VAL):
         zero_helper(i)
         time.sleep(ITER_TIME)
      print("0 off now...")
      time.sleep(SLEEP_TIME)
      # time.sleep(3)
   except Exception as e:
      print(f"Error in zero_off: {e}") 
      
def turn_on(channel):
   global CURRENT_ATT_VALS
   CURRENT_ATT_VALS[channel]=ON_VAL
   try:
      print(f"turning on {channel}...")
      for i in range(71):
         channel_test(71-i,channel)
         time.sleep(ITER_TIME)
      time.sleep(SLEEP_TIME)
      # time.sleep(3)
   except Exception as e:
      print(f"Error in turn_on for channel {channel}: {e}")

# Assuming you have a relay control function like this:
def set_relay_attenuation(attenuation, channel=TALKING_LIGHT_CHANNEL, brighten_channel=0, brighten_value=BRIGHT_IDX):
   global CURRENT_ATT_VALS, bad_write
   if channel >= len(CURRENT_ATT_VALS) or brighten_channel >= len(CURRENT_ATT_VALS):
      print(f"Error: Channel index out of range! channel={channel}, brighten_channel={brighten_channel}")
      return
   # if attenuation >= len(brightness_array):
   #    print(f"Error: Attenuation index out of range! attenuation={attenuation}")
      return
   if brighten_value >= len(brightness_array):
      print(f"Error: Brighten value index out of range! brighten_value={brighten_value}")
      return

   # attenuation_value = brightness_array[attenuation]
   attenuation_value=attenuation

   # Set attenuation for the current channel
   CURRENT_ATT_VALS[channel] = attenuation_value
   
   if brighten_channel!=0 and brighten_channel>0:
      CURRENT_ATT_VALS[brighten_channel]=brightness_array[brighten_value]
      print(f"Setting channel {brighten_channel} to {CURRENT_ATT_VALS[brighten_channel]}")

   message = [
      CHANNEL_BASE, CURRENT_ATT_VALS[0],
      CHANNEL_BASE + 1, CURRENT_ATT_VALS[1],
      CHANNEL_BASE + 2, CURRENT_ATT_VALS[2],
      CHANNEL_BASE + 3, CURRENT_ATT_VALS[3],
   ]
   
   try:
      bus.write_i2c_block_data(DEVICE_ADDRESS, 0, message)
   except Exception as e:
      print(f"  I2C Error on Channel {channel}: {e}")
      bad_write+=1

   # time.sleep(0.1)  # Short delay to smooth transitions

# Function to handle key press and log elapsed time
def log_time_on_space(start_time, output_file, stop_event):
   def on_press(key):
      try:
         if key == keyboard.Key.space:
               elapsed_time = time.time() - start_time
               with open(output_file, 'a') as file:
                  file.write(f"Elapsed time: {elapsed_time:.2f} seconds\n")
               print(f"Logged elapsed time: {elapsed_time:.2f} seconds")
      except Exception as e:
         print(f"Error logging time: {e}")

   # Listener for key presses
   with keyboard.Listener(on_press=on_press) as listener:
      while not stop_event.is_set():
         time.sleep(0.1)  # Keep the listener active
      listener.stop()

# Function to stream audio and process the envelope
def play_and_extract_envelope(file_path, stop_event, output_file, time_file):
   global CURRENT_ATT_VALS, DIM_VAL, BRIGHT_VAL, STOP_EV, OFF_VAL
   try:
      # with wave.open(file_path, 'rb') as wav_file, open(output_file, 'w') as file:
      with open(output_file, 'w') as file:
      
         # # Get audio parameters
         # sample_rate = wav_file.getframerate()
         # num_channels = wav_file.getnchannels()
         # chunk_size = 5600  # Size of chunks to process, was 2800
         # frames_per_buffer = 9640  # Larger buffer for playback stream, was 4820
         
         # # Initialize PyAudio
         # p = pyaudio.PyAudio()
         # stream = p.open(format=p.get_format_from_width(wav_file.getsampwidth()),
         #                   channels=wav_file.getnchannels(),
         #                   rate=wav_file.getframerate(),
         #                   output=True,
         #                   output_device_index=0,
         #                   frames_per_buffer=frames_per_buffer)
         
         # # Pre-fill buffer before playback
         # initial_frames = wav_file.readframes(frames_per_buffer)
         # stream.write(initial_frames)
         
         with open(time_file, 'w') as t_file:
            file.write("Elapsed Time Logs\n")
        
         # Record the start time
         start_time = time.time()
         
         # # Start a thread for monitoring the spacebar press
         # logging_thread = threading.Thread(target=log_time_on_space, args=(start_time, time_file, stop_event))
         # logging_thread.start()
         # threads = [logging_thread]
         
         # thread = threading.Thread(target=turn_on(1))
         # thread.start()  # Start the thread without joining
         # threads.append(thread)  # Add thread to the list
         # print(f"Started thread for space bar logs (non-blocking) ")
         
         channels_set=[0,0,0,0]
         
         # # Initialize pygame mixer
         # pygame.mixer.init()
         # # Load the .wav file
         # pygame.mixer.music.load(file_path)
         # # Play the .wav file
         # pygame.mixer.music.play()
         
         print(f"starting loop... att vals={CURRENT_ATT_VALS}")
         
         # Process audio in chunks
         # while not stop_event.is_set() and pygame.mixer.get_busy():
         # while not stop_event.is_set():
         while STOP_EV==0:
         
            # print(CURRENT_ATT_VALS)
            # frames = wav_file.readframes(chunk_size)
            # if not frames:
            #    break

            # # Play audio
            # stream.write(frames)

            # # Convert frames to a numpy array
            # audio_data = np.frombuffer(frames, dtype=np.int16)

            # # If stereo, take the mean of channels
            # if num_channels == 2:
            #    audio_data = audio_data.reshape(-1, 2).mean(axis=1)

            # # Normalize audio data
            # audio_data = audio_data / np.iinfo(np.int16).max

            # # Calculate RMS value
            # rms = np.sqrt(np.mean(audio_data**2))

            # # Scale RMS to range 0-49
            # scaled_rms = rms * 100  # Adjust scaling factor as needed
            # envelope_value = int(min(max(scaled_rms, 0), 49))

            # Write the envelope value to the text file
            # file.write(f"{envelope_value}\n")
            #  print(f"{envelope_value}\n")
            # Calculate elapsed time
            
            elapsed_time = time.time() - start_time
            # Check if the target duration has passed
            # if elapsed_time % TEST_INTERVAL < 0.1:
            #    print(f"Elapsed time: {elapsed_time:.2f} \n")
            
            
            # Check if the target duration has passed
            
            # STAR
            if elapsed_time >= STAR_ON_TIME:               
               # set_relay_attenuation(envelope_value)
               set_relay_attenuation(random.randint(BRIGHT_VAL, DIM_VAL))
         
            # MARY AND JOSEPH
            if elapsed_time >= CHANNEL_1_B_TIME and channels_set[1] == 0:
               channels_set[1] = 1
               turn_on(1)
               # thread = threading.Thread(target=turn_on, args=(1,))
               # thread.start()  # Start the thread without joining
               # threads.append(thread)  # Add thread to the list
               # print(f"Started thread for channel 1 (non-blocking) at time {elapsed_time}")
               print(f'{channels_set}')
               print(f'{CURRENT_ATT_VALS}')
               # set_relay_attenuation(envelope_value, brighten_channel=1)

            # SHEPHERD
            if elapsed_time >= CHANNEL_2_B_TIME and len(channels_set) > 2 and channels_set[2] == 0:
               channels_set[2] = 1
               turn_on(2)
               # thread = threading.Thread(target=turn_on, args=(2,))
               # thread.start()  # Start the thread without joining
               # threads.append(thread)  # Add thread to the list
               # print(f"Started thread for channel 2 (non-blocking) at time {elapsed_time}")
               print(f'{channels_set}')
               print(f'{CURRENT_ATT_VALS}')
               # set_relay_attenuation(envelope_value, brighten_channel=2)

            # WISEMEN
            if elapsed_time >= CHANNEL_3_B_TIME and len(channels_set) > 3 and channels_set[3] == 0:
               channels_set[3] = 1
               turn_on(3)
               # thread = threading.Thread(target=turn_on, args=(3,))
               # thread.start()  # Start the thread without joining
               # threads.append(thread)  # Add thread to the list
               # print(f"Started thread for channel 3 (non-blocking) at time {elapsed_time}")
               print(f'{channels_set}')
               print(f'{CURRENT_ATT_VALS}')
               # set_relay_attenuation(envelope_value, brighten_channel=3)

            # DIM ALL BUT 1
            # Safely check if dimming should occur
            if elapsed_time >= DIM_TIME and len(channels_set) > 2 and channels_set[2] == 1:
               channels_set[2] = 2
               print(f'{channels_set}')
               print(f'{CURRENT_ATT_VALS}')
               idx_two_three_off()
               # thread = threading.Thread(target=idx_two_three_off)
               # thread.start()  # Start the thread without joining
               # threads.append(thread)  # Add thread to the list
               # print(f"Started thread for channel 2 and 3 (non-blocking) at time {elapsed_time}")
               # temp_0=CURRENT_ATT_VALS[0]
               # temp_1=CURRENT_ATT_VALS[1]
               # CURRENT_ATT_VALS=[temp_0,temp_1,DIM_VAL,DIM_VAL]
               # set_relay_attenuation(envelope_value, brighten_channel=2, brighten_value=DIM_IDX)
               # time.sleep(chunk_size / (sample_rate*3))
               # set_relay_attenuation(envelope_value, brighten_channel=3, brighten_value=DIM_IDX)
               
            # ALL OFF AT END
            if elapsed_time >= ALL_DIM_TIME and len(channels_set) > 3 and channels_set[3] == 1:
               channels_set[3] = 2
               # idx_one_off()
               idx_zero_off()
               CURRENT_ATT_VALS[0]=OFF_VAL
               idx_one_off()
               
               # thread = threading.Thread(target=idx_one_off)
               # thread.start()  # Start the thread without joining
               # threads.append(thread)  # Add thread to the list
               # print(f"Started thread for channel 1 (non-blocking) at time {elapsed_time}")
               # set_all_channels(DIM_IDX)
            
            if elapsed_time>= STOP_TIME:
               print("Stopping")
               # all_off()
               # stop_event.set()
               STOP_EV=1
               break
               
            # Simulate real-time processing (optional)
            # time.sleep(chunk_size / (sample_rate*3))
            time.sleep(0.2)

         # Close the audio stream
         # stream.stop_stream()
         # stream.close()
         # p.terminate()
         # stop_event.set()
         # pygame.mixer.music.stop()
         # for thread in threads:
         #    thread.join()
         # print("All threads have completed. Main program exiting.")
         
         

   except Exception as e:
      print(f"Error in play_and_extract_envelope: {e}")
      # logging_thread.join()
      
      


# Main function
def main():
   global CURRENT_ATT_VALS, STOP_EV, OFF_VAL, SLEEP_TIME
   file_path = "Christmas_Village_Station_2_AUDIO_trimmed.wav"  # Replace with your .wav file path
   output_file = "envelope_values.txt"  # Output file for envelope values
   time_file = "elapsed_times.txt"  # File to log elapsed times

   # stop_event = threading.Event()  # Event to signal threads to stop
   # CURRENT_ATT_VALS=[50,50,50,50]
   # set_all_channels(0)
   all_off()
   #turn_on(0)
   turn_on(1)
   
   try:
      while True:
         button_state = GPIO.input(BUTTON_GPIO)
         if button_state == GPIO.LOW:  # Button is pressed (low)
            GPIO.output(LIGHT_GPIO, GPIO.HIGH)  # Turn the light off
            # Start audio playback and envelope processing in the same thread
            stop_event=0
            # CURRENT_ATT_VALS=[OFF_VAL,OFF_VAL,OFF_VAL,OFF_VAL]
            set_att_vals(OFF_VAL)
            # set_all_channels(0)
            # all_off()
            idx_one_off()
            # time.sleep(1)
            # Initialize pygame mixer
            pygame.mixer.init()
            # Load the .wav file
            pygame.mixer.music.load(file_path)
            # Play the .wav file
            pygame.mixer.music.play()
            time.sleep(1)
            # time.sleep(2)
            play_and_extract_envelope(file_path, stop_event, output_file, time_file)
            while pygame.mixer.get_busy():
               time.sleep(0.1)
            print("loop done")
            # set_att_vals(OFF_VAL)
            # set_all_channels(0)
            time.sleep(7)
            # all_off()
            # turn_on(0)
            turn_on(1)
   
            continue
            # time.sleep(2)
         else:
         #       STOP_EV=0
            GPIO.output(LIGHT_GPIO, GPIO.LOW)  # Turn the light on
         time.sleep(0.1)  # Add a small delay to debounce
      
   except KeyboardInterrupt:
      print("\nKeyboard interrupt received. Exiting gracefully...")
      STOP_EV=1
   except Exception as e:
      print(f"An unexpected error occurred: {e}")
   finally:
      print(f"Envelope values have been saved to {output_file}.")
      # Turn off all channels at the end
      # print("Resetting all channels to 0%% attenuation.")
      # CURRENT_ATT_VALS=[0,0,0,0]
      # set_all_channels(0)
      GPIO.cleanup()

if __name__ == "__main__":
   main()
