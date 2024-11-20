import machine
import time

# I2C configuration
I2C_ADDR = 0x29  # Default I2C address for VL6180
SDA_PIN = 0       # I2C SDA pin (GP0)
SCL_PIN = 1       # I2C SCL pin (GP1)

# Register addresses for VL6180
REG_SYSRANGE_START = 0x04   # Start single-shot range measurement
REG_RESULT_RANGE_VAL = 0x62 # Register for distance result

# Set up I2C on GP0 (SDA) and GP1 (SCL) with a frequency of 50kHz
i2c = machine.I2C(0, sda=machine.Pin(SDA_PIN), scl=machine.Pin(SCL_PIN), freq=50000)

# Main loop to read and print distance
while True:
    try:
        # Trigger a measurement
        i2c.writeto_mem(I2C_ADDR, REG_SYSRANGE_START, bytes([0x01]))
        time.sleep(0.1)  # Wait for the measurement to complete (adjust as needed)

        # Read the result from the VL6180 sensor (2 bytes)
        distance = i2c.readfrom_mem(I2C_ADDR, REG_RESULT_RANGE_VAL, 2)

        # Check if distance is valid
        if len(distance) == 2:
            # Combine the two bytes into a 16-bit distance value
            distance_value = (distance[0] << 8) | distance[1]
            
            # Print the distance in mm
            print(f"Distance: {distance_value} mm")
        else:
            print("Error: Invalid distance data received")

    except Exception as e:
        print("I2C error:", e)

    time.sleep(0.5)  # Delay before the next reading
