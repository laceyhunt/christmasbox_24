# 
#   main.py
#       main pygame loop for nativity light show
#   Scott Denton and Lacey Hunt
#   2023
#

# import threading
# import server
import old_stuff.nativity as nativity
from nativity import bus, get_dimmer_value, bad_write, pygame
import math

# Start the server thread
# server_thread = threading.Thread(target=server.start_server)
# server_thread.daemon = True
# server_thread.start()
    
    

# Pygame loop
state_value=0
running = True
try:
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
    MODE_LIST=[0,0,0,0]
    LAST_MODE_PRESS=[0,0,0,0]
    PRESSED_LIST=[0,0,0,0]
    MAX_LIST=[0,0,0,0]
    CH_PHASE=[0,math.pi/4,2*math.pi/4,3*math.pi/4]
    
    #pygame.mixer.pre_init(32000,-16,2,15000000)
    pygame.init()
    pygame.mixer.init()
    
    # Set up the clock
    clock = pygame.time.Clock()
    key=''
    # state_value=None
    last_state=None
    while (key!='p' and running):
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
        # Check the state value
        if state_value is not None:
            # # Tunnel 1 or Standby LIGHTS OFF 
            # if state_value == '1' or state_value == '4':
            #     print("State value received:", state_value)
            #     nativity.stop_event.set()
            #     if nativity.lightsOff == False:
            #         nativity.lights_off()
            # Nativity Triggered
            if state_value==1:
                if(last_state!=state_value):
                    print("State value received:", state_value)
                    nativity.stop_nativity_threads()
                    nativity.audio_thread, nativity.lights_thread = nativity.start_nativity_threads()
                    # nativity.lights_thread = nativity.start_nativity_threads()
            # Standby LIGHTS ON
            elif state_value == 0:
                print("State value received:", state_value)
                nativity.stop_event.set()
                if nativity.lightsOff == True:
                    nativity.lights_on()        
            # Reset state value
            last_state=state_value
            state_value = None
                  
              
# Keyboard Interrupt
except KeyboardInterrupt:
    print("Pygame loop interrupted")
# Other unknown error
except Exception as e:
    print(f"Unexpected error: {e}")
# Clean up
finally:
    print("Cleaning up...")
    # Signal lights and audio to stop
    nativity.stop_event.set()
    nativity.stop_nativity_threads()

    # # Signal the server thread to stop
    # server.running = False
    # # Join the server thread here so we can exit it with another CTRL-C
    # server_thread.join()
    print("Total Bad Writes: "+str(nativity.bad_write))
    nativity.GPIO.cleanup()
    exit(0)