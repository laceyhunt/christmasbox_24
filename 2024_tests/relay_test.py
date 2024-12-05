import smbus
import time
import math

# Constants
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

# Function to test channels
def test_channels_with_dimmer():
    print("Starting dimmer-based channel test...")
    try:
        for channel in range(4):
            print(f"Testing Channel {channel} with sine wave dimming.")
            start_time = time.time()
            while time.time() - start_time < TEST_DURATION:
                elapsed_time = time.time() - start_time
                dimmer_idx = get_dimmer_value(AMPLITUDE, DIMMER_FREQUENCY, elapsed_time, math.pi * channel / 2)

                if dimmer_idx >= NUM_VALUES:
                    dimmer_idx = NUM_VALUES - 1  # Cap index to valid range

                attenuation_value = brightness_array[dimmer_idx]

                # Set attenuation for the current channel
                attenuation_values = [0, 0, 0, 0]
                attenuation_values[channel] = attenuation_value
                print(f"{attenuation_value}")

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
                    continue

                time.sleep(0.5)  # Short delay to smooth transitions

            print(f"Channel {channel} dimmer test complete.\n")
    except KeyboardInterrupt:
        print("Test interrupted.")
        print(f"Bad writes: {bad_write}")
    finally:
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

# Run the test

def channel_test(test_val):
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
    time.sleep(1)
# test_channels_with_dimmer()
def test():
    # channel_test(0)
    # channel_test(3)
    # channel_test(7)
    
    
    # channel_test(10)
    
    # channel_test(20)
    # channel_test(30)
    # channel_test(40)
    # channel_test(50)
    # channel_test(60)
    # channel_test(71)
    
    # channel_test(0)
    for i in range(71):
        channel_test(71-i)

test()

