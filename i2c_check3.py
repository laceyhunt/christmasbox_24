import smbus
import time
bus=smbus.SMBus(1)
step_size=5
step_delay=0.03
global_atten=60
DEVICE_ADDRESS=0x27
#DEVICE_ADDRESS=0x3f
CHANNEL=0x80
ATTENUATION_LEVEL=global_atten
#message=[CHANNEL1,ATTENUATION_LEVEL]
message=[CHANNEL,ATTENUATION_LEVEL,CHANNEL+1,ATTENUATION_LEVEL,CHANNEL+2,ATTENUATION_LEVEL,CHANNEL+3,ATTENUATION_LEVEL]
try:
    bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
    print("I2C Success")
except:
    print("I2C Fail")
#CHANNEL2=0x81
#ATTENUATION_LEVEL=global_atten
#message2=[CHANNEL2,ATTENUATION_LEVEL]
##bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
#CHANNEL3=0x82
#ATTENUATION_LEVEL=global_atten
#message3=[CHANNEL3,ATTENUATION_LEVEL]
##bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
#CHANNEL4=0x83
#ATTENUATION_LEVEL=global_atten
#message4=[CHANNEL4,ATTENUATION_LEVEL]
#message=message1+message2+message3+message4
#print(message)
#bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
brightness_array=[0,3,7,10,13,14,17,20,23,25,28,30,32,34,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71]
print(len(brightness_array))
if 1:
   for p in range(2000):
       for i in range(len(brightness_array)):
         CHANNEL=0x80
         ATTENUATION_LEVEL=brightness_array[i]
         if ATTENUATION_LEVEL > 70:
            ATTENUATION_LEVEL=100
         
         #message=[CHANNEL,ATTENUATION_LEVEL]
         message=[CHANNEL,ATTENUATION_LEVEL,CHANNEL+1,ATTENUATION_LEVEL,CHANNEL+2,ATTENUATION_LEVEL,CHANNEL+3,ATTENUATION_LEVEL]
         try: 
             bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
             print("I2C Success")
         except:
             print("I2C Fail")
         print("ATTEN: "+str(ATTENUATION_LEVEL))
         time.sleep(step_delay)
       for i in range(len(brightness_array)):
         CHANNEL=0x80
         ATTENUATION_LEVEL=brightness_array[len(brightness_array)-i-1]
         if ATTENUATION_LEVEL > 70:
            ATTENUATION_LEVEL=100
          
         #message=[CHANNEL,int(ATTENUATION_LEVEL)]
         message=[CHANNEL,ATTENUATION_LEVEL,CHANNEL+1,ATTENUATION_LEVEL,CHANNEL+2,ATTENUATION_LEVEL,CHANNEL+3,ATTENUATION_LEVEL]
         
         try: 
             bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
             print("I2C Success")
         except:
             print("I2C Fail")
         print("ATTEN: "+str(ATTENUATION_LEVEL))
         time.sleep(step_delay)
