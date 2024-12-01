import struct
import time
from machine import Pin
from machine import SoftI2C
from sensor import Sensor

I2C_ADDR1 = 0x29  # I2C address for the first sensor
I2C_ADDR2 = 0x30  # Changed I2C address for the second sensor (must be different)
SDA_PIN_0 = 0      # I2C SDA pin for the first sensor (GP0)
SCL_PIN_0 = 1      # I2C SCL pin for the first sensor (GP1)
SDA_PIN_1 = 2      # I2C SDA pin for the second sensor (GP2)
SCL_PIN_1 = 3      # I2C SCL pin for the second sensor (GP3)

# Set up I2C on GP0 (SDA) and GP1 (SCL) for the first sensor
i2c_0 = SoftI2C(sda=Pin(SDA_PIN_0), scl=Pin(SCL_PIN_0), freq=50000)

# Set up I2C on GP2 (SDA) and GP3 (SCL) for the second sensor
i2c_1 = SoftI2C(sda=Pin(SDA_PIN_1), scl=Pin(SCL_PIN_1), freq=50000)

# Initialize the two sensors with different I2C addresses
sensor1 = Sensor(i2c_0, addr=I2C_ADDR1)
sensor2 = Sensor(i2c_1, addr=I2C_ADDR2)

# Main loop to read and print distance for both sensors
def sensordata():
    while True:
        # Read the distance from the first sensor
        distance1 = sensor1.range()
        print("Sensor 1 distance: {}mm".format(distance1))

        # Read the distance from the second sensor
        distance2 = sensor2.range()
        print("Sensor 2 distance: {}mm".format(distance2))

        time.sleep(1)  # Delay before the next reading

# Call the function to start reading data
sensordata()
