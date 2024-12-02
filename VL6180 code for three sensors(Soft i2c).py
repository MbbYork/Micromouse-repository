import struct
import time
from machine import Pin
from machine import SoftI2C
from sensor import Sensor

I2C_ADDRF = 0x29  # I2C address for the first sensor
I2C_ADDRL = 0x30 # Changed I2C address for the second sensor (must be different)
I2C_ADDRR = 0x31
SDA_PIN_F = 0      # I2C SDA pin for the first sensor (GP0)
SCL_PIN_F = 1      # I2C SCL pin for the first sensor (GP1)
SDA_PIN_L = 2      # I2C SDA pin for the second sensor (GP2)
SCL_PIN_L = 3      # I2C SCL pin for the second sensor (GP3)
SDA_PIN_R = 4
SCL_PIN_R = 5

# Set up I2C on GP0 (SDA) and GP1 (SCL) for the first sensor
i2c_F = SoftI2C(sda=Pin(SDA_PIN_F), scl=Pin(SCL_PIN_F), freq=50000)

# Set up I2C on GP2 (SDA) and GP3 (SCL) for the second sensor
i2c_L = SoftI2C(sda=Pin(SDA_PIN_L), scl=Pin(SCL_PIN_L), freq=50000)

i2c_R = SoftI2C(sda=Pin(SDA_PIN_R), scl=Pin(SCL_PIN_R), freq=50000)

# Initialize the two sensors with different I2C addresses
sensorF = Sensor(i2c_F)
sensorL = Sensor(i2c_L)
sensorR = Sensor(i2c_R)
# Main loop to read and print distance for both sensors
def sensordata():
    while True:
        # Read the distance from the first sensor
        distanceF = sensorF.range()
        print("Front Sensor distance: {}mm".format(distanceF))

        # Read the distance from the second sensor
        distanceL = sensorL.range()
        print("Left sensor distance: {}mm".format(distanceL))
        
        distanceR = sensorR.range()
        print("Right sensor distance: {}mm".format(distanceR))

        time.sleep(1)  # Delay before the next reading

# Call the function to start reading data
sensordata()
