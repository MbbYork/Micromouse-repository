import struct
import time
import machine
from sensor import Sensor

I2C_ADDR1 = 0x29  # I2C address for the first sensor
I2C_ADDR2 = 0x30  # I2C address for the second sensor
SDA_PIN = 0       # I2C SDA pin (GP0)
SCL_PIN = 1       # I2C SCL pin (GP1)

# Set up I2C on GP0 (SDA) and GP1 (SCL) with a frequency of 50kHz
i2c = machine.I2C(0, sda=machine.Pin(SDA_PIN), scl=machine.Pin(SCL_PIN), freq=50000)

# Initialize the two sensors with different addresses
sensor1 = Sensor(i2c, I2C_ADDR1)
sensor2 = Sensor(i2c, I2C_ADDR2)

# Main loop to read and print distance for both sensors
while True:
    # Read the distance from the first sensor
    distance1 = sensor1.range()
    print("Sensor 1 distance: {}mm".format(distance1))
    
    # Read the distance from the second sensor
    distance2 = sensor2.range()
    print("Sensor 2 distance: {}mm".format(distance2))
    
    time.sleep(1)  # Delay before the next reading
