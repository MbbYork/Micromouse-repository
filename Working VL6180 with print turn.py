import struct
import time
from machine import I2C
from sensor import Sensor

I2C_ADDR = 0x29  # Default I2C address for VL6180
SDA_PIN = 0       # I2C SDA pin (GP0)
SCL_PIN = 1     # I2C SCL pin (GP1)


# Set up I2C on GP0 (SDA) and GP1 (SCL) with a very low frequency (25kHz)
i2c = machine.I2C(0, sda=machine.Pin(SDA_PIN), scl=machine.Pin(SCL_PIN), freq=50000)

sensor=Sensor(i2c)

# Main loop to read and print distance
while True:
    distance = sensor.range()  # Make sure this method is correct
    print("distance:{}mm".format(distance))
    
    if distance >= 50:  # Corrected typo from 'ditance' to 'distance'
        print("Turn")
    
    time.sleep(1)  # Delay before the next reading

    
