import threading
import time
from pynput import keyboard

# Your turn_on function
def turn_on(channel):
    try:
        print(f"turning on channel {channel}...")
        for i in range(71):
            # Simulate channel adjustment
            print(f"Adjusting channel {channel}: {71 - i}")
            time.sleep(0.01)  # Simulates work being done
        print(f"Channel {channel} is fully turned on.")
    except Exception as e:
        print(f"Error in turn_on for channel {channel}: {e}")

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

# Main function with threading
def main():
    intervals = [3, 5, 10]  # Time intervals to start threads
    channels = [1, 2, 3]    # Channels to pass to turn_on function
    output_file = "elapsed_times.txt"  # File to log elapsed times
    start_time = time.time()
    stop_event = threading.Event()

    # Ensure the file is created/cleared at the start
    with open(output_file, 'w') as file:
        file.write("Elapsed Time Logs\n")

    # Start a thread for monitoring the spacebar press
    logging_thread = threading.Thread(target=log_time_on_space, args=(start_time, output_file, stop_event))
    logging_thread.start()

    # List to keep track of threads
    threads = [logging_thread]

    if len(intervals) != len(channels):
        print("Error: intervals and channels lists must be of the same length.")
        return

    for i, interval in enumerate(intervals):
        channel = channels[i]
        print(f"Waiting {interval} seconds to start thread for channel {channel}...")
        time.sleep(interval)  # Wait for the specified interval

        # Create and start the thread
        thread = threading.Thread(target=turn_on, args=(channel,))
        thread.start()  # Start the thread without joining
        threads.append(thread)  # Add thread to the list
        print(f"Started thread for channel {channel} (non-blocking)")

    # Signal the logging thread to stop
    stop_event.set()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("All threads have completed. Main program exiting.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated.")
