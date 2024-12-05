import wave
import numpy as np
import pyaudio
import threading
import time
import smbus
# import RPi.GPIO as GPIO

# Pin setup
BUTTON_GPIO = 20  # Button pin
LIGHT_GPIO = 21   # Light pin

# GPIO setup
# GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
# GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button as input with pull-up
# GPIO.setup(LIGHT_GPIO, GPIO.OUT)  # Light as output

# index of brightness_array that the non-star values go to when they are on
BRIGHT_VAL=71
BRIGHT_IDX=49
DIM_VAL=50
DIM_IDX=28
# Set the target duration in seconds
CHANNEL_1_B_TIME = 40
CHANNEL_2_B_TIME = 70
CHANNEL_3_B_TIME = 80
DIM_TIME = 95
ALL_DIM_TIME = 100
TEST_INTERVAL=2

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

AMPLITUDE = len(brightness_array) // 2  # Maximum amplitude for dimmer values
bad_write=0
# I2C bus setup
bus = smbus.SMBus(1)  # Use 0 for older Raspberry Pi models


def set_all_channels(test_val):
   global bad_write
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
      bad_write+=1
    
# Write an initial value for the lights to turn everything on
# ATTENUATION_LEVEL=0
# set_all_channels(0)
# message=[CHANNEL_BASE,ATTENUATION_LEVEL,CHANNEL_BASE+1,ATTENUATION_LEVEL,CHANNEL_BASE+2,ATTENUATION_LEVEL,CHANNEL_BASE+3,ATTENUATION_LEVEL]
# # Wrap a try except around the I2C write so we dont exit if there is an I2C error.
# try:
#    bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
#    print("set to 0")
#    time.sleep(3)
# except:
#    bad_write+=1
#    print("I2C ERROR")

# start values   
attenuation_values = [0, 0, 0, 0]    
NUM_VALUES = len(brightness_array)

# Assuming you have a relay control function like this:
def set_relay_attenuation(attenuation, channel=TALKING_LIGHT_CHANNEL, brighten_channel=0, brighten_value=BRIGHT_IDX):
   global attenuation_values, bad_write
   # This function adjusts the attenuation for the specified channel
   # The actual implementation of this will depend on your relay setup
   #print(f"Setting attenuation of channel {channel} to {attenuation}%")
   if channel >= len(attenuation_values) or brighten_channel >= len(attenuation_values):
      print(f"Error: Channel index out of range! channel={channel}, brighten_channel={brighten_channel}")
      return
   if attenuation >= len(brightness_array):
      print(f"Error: Attenuation index out of range! attenuation={attenuation}")
      return

   if brighten_value >= len(brightness_array):
      print(f"Error: Brighten value index out of range! brighten_value={brighten_value}")
      return

   # if 0 <= brighten_channel < len(attenuation_values):
   #    attenuation_values[brighten_channel] = brightness_array[brighten_value]
   #    print(f"Setting channel {brighten_channel} to {attenuation_values[brighten_channel]}")
   # else:
   #    print(f"Invalid brighten_channel: {brighten_channel}")

   attenuation_value = brightness_array[attenuation]

   # Set attenuation for the current channel
   attenuation_values[channel] = attenuation_value
   
   if brighten_channel!=0 and brighten_channel>0:
      attenuation_values[brighten_channel]=brightness_array[brighten_value]
      print(f"Setting channel {brighten_channel} to {attenuation_values[brighten_channel]}")

   message = [
      CHANNEL_BASE, attenuation_values[0],
      CHANNEL_BASE + 1, attenuation_values[1],
      CHANNEL_BASE + 2, attenuation_values[2],
      CHANNEL_BASE + 3, attenuation_values[3],
   ]
   
   try:
      bus.write_i2c_block_data(DEVICE_ADDRESS, 0, message)
   except Exception as e:
      print(f"  I2C Error on Channel {channel}: {e}")
      bad_write+=1

   # time.sleep(0.1)  # Short delay to smooth transitions
   
# Function to stream audio and process the envelope
def play_and_extract_envelope(file_path, stop_event, output_file):
   global attenuation_values
   try:
      print(f"starting loop... att vals={attenuation_values}")
      with wave.open(file_path, 'rb') as wav_file, open(output_file, 'w') as file:
         # Get audio parameters
         sample_rate = wav_file.getframerate()
         num_channels = wav_file.getnchannels()
         chunk_size = 2800  # Size of chunks to process
         frames_per_buffer = 4820  # Larger buffer for playback stream
         
         # Initialize PyAudio
         p = pyaudio.PyAudio()
         stream = p.open(format=p.get_format_from_width(wav_file.getsampwidth()),
                           channels=wav_file.getnchannels(),
                           rate=wav_file.getframerate(),
                           output=True,
                           output_device_index=0,
                           frames_per_buffer=frames_per_buffer)
         
         # Pre-fill buffer before playback
         initial_frames = wav_file.readframes(frames_per_buffer*2)
         stream.write(initial_frames)
         
         # Record the start time
         start_time = time.time()
         
         channels_set=[0,0,0,0]
         # Process audio in chunks
         while not stop_event.is_set():
            frames = wav_file.readframes(chunk_size)
            if not frames:
               break

            # Play audio
            stream.write(frames)

            # Convert frames to a numpy array
            audio_data = np.frombuffer(frames, dtype=np.int16)

            # If stereo, take the mean of channels
            if num_channels == 2:
               audio_data = audio_data.reshape(-1, 2).mean(axis=1)

            # Normalize audio data
            audio_data = audio_data / np.iinfo(np.int16).max

            # Calculate RMS value
            rms = np.sqrt(np.mean(audio_data**2))

            # Scale RMS to range 0-49
            scaled_rms = rms * 100  # Adjust scaling factor as needed
            envelope_value = int(min(max(scaled_rms, 0), 49))

            # Write the envelope value to the text file
            # file.write(f"{envelope_value}\n")
            #  print(f"{envelope_value}\n")
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            # Check if the target duration has passed
            # Print the elapsed time every 'interval' seconds
            if elapsed_time % TEST_INTERVAL < 0.1:
               print(f"Elapsed time: {elapsed_time:.2f} \n")
            
            
            # Check if the target duration has passed
            if elapsed_time >= CHANNEL_1_B_TIME and channels_set[1] == 0:
               channels_set[1] = 1
               print(f'{channels_set}')
               print(f'{attenuation_values}')
               
               set_relay_attenuation(envelope_value, brighten_channel=1)

            if elapsed_time >= CHANNEL_2_B_TIME and len(channels_set) > 2 and channels_set[2] == 0:
               channels_set[2] = 1
               print(f'{channels_set}')
               print(f'{attenuation_values}')
               
               set_relay_attenuation(envelope_value, brighten_channel=2)

            if elapsed_time >= CHANNEL_3_B_TIME and len(channels_set) > 3 and channels_set[3] == 0:
               channels_set[3] = 1
               print(f'{channels_set}')
               print(f'{attenuation_values}')
               
               set_relay_attenuation(envelope_value, brighten_channel=3)

            # Safely check if dimming should occur
            if elapsed_time >= DIM_TIME and len(channels_set) > 2 and channels_set[2] == 1:
               channels_set[2] = 2
               print(f'{channels_set}')
               print(f'{attenuation_values}')
               
               # temp_0=attenuation_values[0]
               # temp_1=attenuation_values[1]
               # attenuation_values=[temp_0,temp_1,DIM_VAL,DIM_VAL]
               set_relay_attenuation(envelope_value, brighten_channel=2, brighten_value=DIM_IDX)
               time.sleep(chunk_size / (sample_rate*3))
               set_relay_attenuation(envelope_value, brighten_channel=3, brighten_value=DIM_IDX)

            if elapsed_time >= ALL_DIM_TIME and len(channels_set) > 3 and channels_set[3] == 1:
               channels_set[3] = 2
               set_all_channels(DIM_IDX)
            else:               
               set_relay_attenuation(envelope_value)
         
            # Simulate real-time processing (optional)
            time.sleep(chunk_size / (sample_rate*3))

         # Close the audio stream
         stream.stop_stream()
         stream.close()
         p.terminate()

   except Exception as e:
      print(f"Error in play_and_extract_envelope: {e}")

# Main function
def main():
   global attenuation_values
   file_path = "Christmas_Village_Station_2_AUDIO.wav"  # Replace with your .wav file path
   output_file = "envelope_values.txt"  # Output file for envelope values

   stop_event = threading.Event()  # Event to signal threads to stop
   # attenuation_values=[50,50,50,50]
   set_all_channels(0)
   
   try:
      while True:
        button_state = GPIO.input(BUTTON_GPIO)
        if button_state == GPIO.LOW:  # Button is pressed (low)
            GPIO.output(LIGHT_GPIO, GPIO.HIGH)  # Turn the light off
            # Start audio playback and envelope processing in the same thread
            attenuation_values=[46,46,46,46]
            set_all_channels(DIM_VAL)
            time.sleep(2)
            play_and_extract_envelope(file_path, stop_event, output_file)
            # time.sleep(2)
        else:
            GPIO.output(LIGHT_GPIO, GPIO.LOW)  # Turn the light on
        time.sleep(0.1)  # Add a small delay to debounce
      
   except KeyboardInterrupt:
      print("\nKeyboard interrupt received. Exiting gracefully...")
      stop_event.set()
   except Exception as e:
      print(f"An unexpected error occurred: {e}")
   finally:
      print(f"Envelope values have been saved to {output_file}.")
      # Turn off all channels at the end
      print("Resetting all channels to 0%% attenuation.")
      attenuation_values=[0,0,0,0]
      set_all_channels(0)
      GPIO.cleanup()

if __name__ == "__main__":
   main()
