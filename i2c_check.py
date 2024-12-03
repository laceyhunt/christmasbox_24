import smbus
import time
bus=smbus.SMBus(1)

global_atten=0
DEVICE_ADDRESS=0x27
#DEVICE_ADDRESS=0x3f
CHANNEL=0x80
ATTENUATION_LEVEL=global_atten
message=[CHANNEL,ATTENUATION_LEVEL]
bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
CHANNEL=0x81
ATTENUATION_LEVEL=global_atten
message=[CHANNEL,ATTENUATION_LEVEL]
bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
CHANNEL=0x82
ATTENUATION_LEVEL=global_atten
message=[CHANNEL,ATTENUATION_LEVEL]
bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
CHANNEL=0x83
ATTENUATION_LEVEL=global_atten
message=[CHANNEL,ATTENUATION_LEVEL]
bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)

if 0:
   for p in range(10):
      for i in range(10):
         CHANNEL=0x80
         ATTENUATION_LEVEL=i*10
         
         message=[CHANNEL,ATTENUATION_LEVEL]
         
         bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
         print("ATTEN: "+str(ATTENUATION_LEVEL))
         time.sleep(0.5)
      for i in range(10):
         CHANNEL=0x80
         ATTENUATION_LEVEL=100-(i*10)
         
         message=[CHANNEL,ATTENUATION_LEVEL]
         
         bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
         print("ATTEN: "+str(ATTENUATION_LEVEL))
         time.sleep(0.5)
