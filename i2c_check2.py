import smbus
import time
bus=smbus.SMBus(1)

global_atten=99
DEVICE_ADDRESS=0x27
#DEVICE_ADDRESS=0x3f
CHANNEL1=0x80
ATTENUATION_LEVEL=global_atten
message1=[CHANNEL1,ATTENUATION_LEVEL]
#bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
CHANNEL2=0x81
ATTENUATION_LEVEL=global_atten
message2=[CHANNEL2,ATTENUATION_LEVEL]
#bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
CHANNEL3=0x82
ATTENUATION_LEVEL=global_atten
message3=[CHANNEL3,ATTENUATION_LEVEL]
#bus.write_i2c_block_data(DEVICE_ADDRESS,0,message)
CHANNEL4=0x83
ATTENUATION_LEVEL=global_atten
message4=[CHANNEL4,ATTENUATION_LEVEL]
message=message1+message2+message3+message4
print(message)
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
