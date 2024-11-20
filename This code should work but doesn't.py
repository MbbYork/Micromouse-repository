import machine
import time

# I2C configuration
I2C_ADDR = 0x29  # Default I2C address for VL6180
SDA_PIN = 0       # I2C SDA pin (GP0)
SCL_PIN = 1       # I2C SCL pin (GP1)

# Register addresses for VL6180
REG_SYSRANGE_START = 0x01
REG_RESULT_RANGE_VAL = 0x62

# Set up I2C on GP0 (SDA) and GP1 (SCL) with a very low frequency (25kHz)
i2c = machine.I2C(0, sda=machine.Pin(SDA_PIN), scl=machine.Pin(SCL_PIN), freq=50000)

# Main loop to read and print distance
while True:
    try:
        # Trigger a measurement
        i2c.writeto_mem(I2C_ADDR, REG_SYSRANGE_START, bytes([0x01]))
        time.sleep(0.05)  # Wait for the measurement to complete

        # Read the result from the VL6180 sensor (1 byte)
        distance = i2c.readfrom_mem(I2C_ADDR, REG_RESULT_RANGE_VAL, 1)
        print(f"Distance: {distance[0]} mm")  # Print the distance in mm

    except Exception as e:
        print("I2C error:", e)

    time.sleep(0.5)  # Delay before the next reading
