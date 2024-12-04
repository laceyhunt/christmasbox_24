# 
#   main.py
#       main pygame loop for nativity light show
#   Scott Denton and Lacey Hunt
#   2023
#

# import threading
# import server
import old_stuff.nativity as nativity
# from nativity import bus, get_dimmer_value, bad_write

# Start the server thread
# server_thread = threading.Thread(target=server.start_server)
# server_thread.daemon = True
# server_thread.start()
    
    

# Pygame loop
state_value=0
running = True
try:
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
    
    # state_value=None
    last_state=None
    while (key!='p' and running):
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
            nativity.bad_write+=1
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