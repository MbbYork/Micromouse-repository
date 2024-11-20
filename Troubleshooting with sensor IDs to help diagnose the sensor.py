import machine
import time

# I2C configuration
I2C_ADDR = 0x29  # Default I2C address for VL6180
SDA_PIN = 0       # I2C SDA pin (GP0)
SCL_PIN = 1       # I2C SCL pin (GP1)

# Register addresses for VL6180
REG_SYSRANGE_START = 0x18    # Start single-shot range measurement
REG_RESULT_RANGE_VAL = 0x62  # Register for distance result
REG_SYSRANGE_STATUS = 0x04   # Register for status flags

# Identification registers
REG_IDENTIFICATION_MODEL_ID = 0x00  # Model ID register
REG_IDENTIFICATION_REVISION_ID = 0x01  # Revision ID register
REG_IDENTIFICATION_PART_ID = 0x02  # Part ID register

# Set up I2C on GP0 (SDA) and GP1 (SCL) with a frequency of 50kHz
i2c = machine.I2C(0, sda=machine.Pin(SDA_PIN), scl=machine.Pin(SCL_PIN), freq=50000)

# Function to check the sensor status
def check_sensor_status():
    try:
        # Read the status register (1 byte)
        status = i2c.readfrom_mem(I2C_ADDR, REG_SYSRANGE_STATUS, 1)
        
        # Check if the "range ready" bit (bit 0) is set
        if status[0] & 0x01:
            print("Sensor is ready for a new measurement")
        else:
            print("Sensor is not ready")
        
        # Check if there's an error (bit 3)
        if status[0] & 0x08:
            print("Sensor error detected")
        else:
            print("No sensor error")

    except Exception as e:
        print("Error checking sensor status:", e)

# Function to read identification registers
def read_identification():
    try:
        # Read the model, revision, and part ID
        model_id = i2c.readfrom_mem(I2C_ADDR, REG_IDENTIFICATION_MODEL_ID, 1)
        revision_id = i2c.readfrom_mem(I2C_ADDR, REG_IDENTIFICATION_REVISION_ID, 1)
        part_id = i2c.readfrom_mem(I2C_ADDR, REG_IDENTIFICATION_PART_ID, 1)
        
        # Print out the identification details
        print(f"Model ID: {model_id[0]}")
        print(f"Revision ID: {revision_id[0]}")
        print(f"Part ID: {part_id[0]}")

    except Exception as e:
        print("Error reading identification registers:", e)

# Main loop to read and print distance
while True:
    try:
        # Trigger a measurement
        i2c.writeto_mem(I2C_ADDR, REG_SYSRANGE_START, bytes([0x01]))
        time.sleep(0.2)  # Wait for the measurement to complete (increased delay)

        # Check the sensor status
        check_sensor_status()

        # Read the result from the VL6180 sensor (2 bytes)
        distance = i2c.readfrom_mem(I2C_ADDR, REG_RESULT_RANGE_VAL, 2)

        # Print the raw bytes read from the sensor
        print(f"Raw data (bytes): {distance}")

        # Combine the two bytes into a 16-bit distance value
        distance_value = (distance[0] << 8) | distance[1]
        
        # Print the distance in mm
        print(f"Distance: {distance_value} mm")

        # Check for invalid distances (example threshold for invalid readings)
        if distance_value == 16128:
            print("Invalid reading or out-of-range detected!")

    except Exception as e:
        print("I2C error:", e)

    # Read and print the sensor identification information (to verify sensor)
    read_identification()

    time.sleep(0.5)  # Delay before the next reading
