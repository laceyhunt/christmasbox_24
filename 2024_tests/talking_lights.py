import pygame
import math
import threading
import smbus
import time
import numpy as np
import wave 

# i2c stuff
# Constants
talking_light_channel=0
TEST_DURATION=10
DEVICE_ADDRESS = 0x27  # Replace with your I2C device address
CHANNEL_BASE = 0x80       # Adjust if your channels start from a different base
TEST_DURATION = 10     # Test duration for each channel in seconds
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

# Write an initial value for the lights to turn everything on
ATTENUATION_LEVEL=0
message=[CHANNEL_BASE,ATTENUATION_LEVEL,CHANNEL_BASE+1,ATTENUATION_LEVEL,CHANNEL_BASE+2,ATTENUATION_LEVEL,CHANNEL_BASE+3,ATTENUATION_LEVEL]
# Wrap a try except around the I2C write so we dont exit if there is an I2C error.
try:
    bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
except:
    bad_write+=1
    print("I2C ERROR")
    
NUM_VALUES = len(brightness_array)
# Function to get the dimmer value
def get_dimmer_value(amplitude, frequency, time, phase):
    scaled_amplitude = min(amplitude, NUM_VALUES // 2)
    sine_value = math.sin(2 * math.pi * frequency * time + phase)
    dimmer_value = int((sine_value + 1) / 2 * (2 * scaled_amplitude))
    return dimmer_value

# Event to control stopping the audio
stop_event = threading.Event()

# Assuming you have a relay control function like this:
def set_relay_attenuation(attenuation, channel=talking_light_channel):
   # This function adjusts the attenuation for the specified channel
   # The actual implementation of this will depend on your relay setup
#    print(f"Setting attenuation of channel {channel} to {attenuation}%")

   attenuation_value = brightness_array[attenuation]

   # Set attenuation for the current channel
   attenuation_values = [0, 0, 0, 0]
   attenuation_values[channel] = attenuation_value

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

   time.sleep(0.1)  # Short delay to smooth transitions


def play_audio(file_path, stop_event):
    try:
        # Start mixer
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() and not stop_event.is_set():
            time.sleep(0.1)

        # # Create a clock to manage the loop
        # clock = pygame.time.Clock()

        # # Play while audio is still going and stop_event is not set
        # while pygame.mixer.music.get_busy() and not stop_event.is_set():
        #     # Get the audio envelope
        #     envelope, chunk_size, sample_rate = extract_envelope()
            
        #     # Adjust attenuation for the first relay channel based on the envelope
        #     attenuation = min(envelope, NUM_VALUES)  # Ensure it doesn't go beyond threshold
        #     set_relay_attenuation(attenuation)
            
        #     # Simulate real-time processing
        #     time.sleep(chunk_size / sample_rate)
        #     # Wait for a short period before checking again (30 FPS)
        #     # clock.tick(30)

    # except KeyboardInterrupt
    except Exception as e:
        print(f"Error in play_audio: {e}")
        print("\nAudio playback interrupted. Stopping the audio gracefully...")

    finally:
        # Stop audio and reset relay settings in case of interruption
        pygame.mixer.music.stop()
        # set_relay_attenuation(0)  # Reset attenuation of channel 0
        pygame.mixer.quit()
        print("Audio playback stopped.")
        # Turn off all channels at the end
        print("Resetting all channels to 0% attenuation.")
        reset_message = [
            CHANNEL_BASE, 0,
            CHANNEL_BASE + 1, 0,
            CHANNEL_BASE + 2, 0,
            CHANNEL_BASE + 3, 0,
        ]
        try:
            bus.write_i2c_block_data(DEVICE_ADDRESS, 0, reset_message)
        except Exception as e:
            print(f"Error resetting channels: {e}")


# Function to extract and process the sound envelope
def extract_envelope(file_path, output_file, stop_event):
    try: 
        with wave.open(file_path, 'rb') as wav_file, open(output_file, 'w') as file:
            # Get audio parameters
            sample_rate = wav_file.getframerate()
            num_channels = wav_file.getnchannels()
            chunk_size = 1024  # Size of chunks to process
            
            # Process each chunk
            while not stop_event.is_set():
                # Read a chunk of frames
                frames = wav_file.readframes(chunk_size)
                if not frames:
                    break
                
                # Convert frames to a numpy array
                audio_data = np.frombuffer(frames, dtype=np.int16)
                # normalize audio for better range
                audio_data = audio_data / np.iinfo(np.int16).max
                
                # If stereo, take the mean of channels
                if num_channels == 2:
                    audio_data = audio_data.reshape(-1, 2).mean(axis=1)
                
                # Calculate RMS value
                rms = np.sqrt(np.mean(audio_data**2))
                # amplify and scale rms for scaling
                scaled_rms = rms * 100  # Example scaling factor
                # envelope_value = int(min(scaled_rms, 49))
                envelope_value = int(min(max(scaled_rms, 0), 49))

                
                # Scale RMS to range 0-49
                # envelope_value = int((rms / np.iinfo(np.int16).max) * 49)
                attenuation = envelope_value
                # attenuation=min(attenuation, 49)
                # attenuation*=10
                
                # Print the envelope value
                # if envelope_value != 0:
                file.write(f"Envelope: {envelope_value}, Attenuation: {attenuation}\n")
                print(f"Envelope: {envelope_value}, Attenuation: {attenuation}\n")
                # print(f"Envelope Value: {envelope_value}")
                # attenuation = min(envelope_value, NUM_VALUES)  # Ensure it doesn't go beyond threshold
                set_relay_attenuation(attenuation)
                # return envelope_value, chunk_size, sample_rate
                
                # Simulate real-time processing
                time.sleep(chunk_size / sample_rate)
    except Exception as e:
        print(f"Error in extract_envelope: {e}")

# Example usage:
# Play the audio and adjust attenuation during playback
# play_audio('Christmas_Village_Station_2_AUDIO.wav')


# Main function
def main():
    file_path = "Christmas_Village_Station_2_AUDIO.wav"  # Replace with your .wav file path
    output_file = "envelope_values.txt"  # Output file for envelope values
    stop_event = threading.Event()  # Event to signal threads to stop
    
    try: 
        # Start audio playback in a separate thread
        audio_thread = threading.Thread(target=play_audio, args=(file_path,stop_event))
        audio_thread.start()
        
        # Start envelope extraction
        envelope_thread = threading.Thread(target=extract_envelope, args=(file_path,output_file,stop_event))
        envelope_thread.start()

        # Join threads back to the main program
        audio_thread.join()
        envelope_thread.join()
    
        print("Audio playback and envelope extraction complete.")
        
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting gracefully...")
        stop_event.set()  # Signal threads to stop
        # Allow threads to check stop_event and exit
        time.sleep(0.5)
        # Join threads safely
        audio_thread.join(timeout=1)
        envelope_thread.join(timeout=1)
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    finally:
        print("Program terminated.")
        
        
if __name__ == "__main__":
    main()