import pygame
import wave
import numpy as np
import threading
import time

# Function to play the .wav file
def play_audio(file_path):
   try: 
      pygame.mixer.init()
      pygame.mixer.music.load(file_path)
      pygame.mixer.music.play()
      # Keep thread alive while audio is playing
      while pygame.mixer.music.get_busy():
         time.sleep(0.1)
   except Exception as e:
      print(f"Error in play_audio: {e}")
   finally:
      pygame.mixer.quit()  # Clean up pygame resources
      
# Function to extract and process the sound envelope
def extract_envelope(file_path):
   try: 
      with wave.open(file_path, 'rb') as wav_file:
         # Get audio parameters
         sample_rate = wav_file.getframerate()
         num_channels = wav_file.getnchannels()
         chunk_size = 1024  # Size of chunks to process
         
         # Process each chunk
         while True:
            # Read a chunk of frames
            frames = wav_file.readframes(chunk_size)
            if not frames:
                  break
            
            # Convert frames to a numpy array
            audio_data = np.frombuffer(frames, dtype=np.int16)
            
            # If stereo, take the mean of channels
            if num_channels == 2:
                  audio_data = audio_data.reshape(-1, 2).mean(axis=1)
            
            # Calculate RMS value
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Scale RMS to range 0-49
            envelope_value = int((rms / np.iinfo(np.int16).max) * 49)
            envelope_value = min(max(envelope_value, 0), 49)
            
            # Print the envelope value
            print(f"Envelope Value: {envelope_value}")
            
            # Simulate real-time processing
            time.sleep(chunk_size / sample_rate)
   except Exception as e:
      print(f"Error in extract_envelope: {e}")

# Main function
def main():
   file_path = "Christmas_Village_Station_2_AUDIO.wav"  # Replace with your .wav file path
   
   stop_event = threading.Event()  # Event to signal threads to stop

   try: 
      # Start audio playback in a separate thread
      audio_thread = threading.Thread(target=play_audio, args=(file_path,))
      audio_thread.start()
      
      # Start envelope extraction
      envelope_thread = threading.Thread(target=extract_envelope, args=(file_path,))
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
