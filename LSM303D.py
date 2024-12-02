from machine import UART, Pin, SoftI2C
import time
import sys
from math import atan2, pi
from machine import I2C


class LSM303D:
    """
    LSM303D Magnetometer Class
    """

    def __init__(self, sda_pin, scl_pin, addr=0x1E):
        """
        Initializes the LSM303D sensor.

        Args:
            sda_pin (int): Pin connected to the I2C SDA line.
            scl_pin (int): Pin connected to the I2C SCL line.
            addr (int, optional): I2C address of the sensor (default: 0x1E).
        """
        self.i2c = I2C(1, sda=sda_pin, scl=scl_pin, freq=100000)
        self.addr = addr

        # Configure the LSM303D
        self.write_register(0x20, 0x57)  # Control register 1: 50Hz, enable X, Y, Z
        self.write_register(0x21, 0x00)  # Control register 2: Continuous conversion mode, high-resolution
        self.write_register(0x22, 0x00)  # Control register 3: Default configuration
        self.write_register(0x23, 0x00)  # Control register 4: Default configuration
        self.write_register(0x24, 0x00)  # Control register 5: Default configuration

    def write_register(self, reg_addr, data):
        """
        Writes data to a specific register on the sensor.

        Args:
            reg_addr (int): Register address.
            data (bytearray): Data to write.
        """
        self.i2c.writeto_mem(self.addr, reg_addr, data)

    def read_axis(self, reg_addr):
        """
        Reads a 16-bit signed value from a register.

        Args:
            reg_addr (int): Register address (X, Y, or Z).

        Returns:
            float: Signed floating-point value representing the axis reading.
        """
        high = bytearray(1)
        low = bytearray(1)
        self.i2c.readfrom_mem_into(self.addr, reg_addr, low)
        self.i2c.readfrom_mem_into(self.addr, reg_addr + 1, high)
        res = high[0] * 256 + low[0]
        if res < 16384:
            result = res / 16384.0
        elif res >= 16384 and res < 49152:
            result = (32768 - res) / 16384.0
        else:
            result = (res - 65536) / 16384.0
        return result

    def get_mag_x(self):
        """
        Reads the X-axis magnetic field value.

        Returns:
            int: Signed integer representing the X-axis magnetic field.
        """
        data = self.read_axis(0x08)
        if data > 32767:
            data -= 65536
        return data

    def get_mag_y(self):
        """
        Reads the Y-axis magnetic field value.

        Returns:
            int: Signed integer representing the Y-axis magnetic field.
        """
        return self.read_axis(0x0A)

    def get_mag_z(self):
        """
        Reads the Z-axis magnetic field value.

        Returns:
            int: Signed integer representing the Z-axis magnetic field.
        """
        return self.read_axis(0x0C)

    def get_heading(self):
        """
        Calculates the heading in degrees based on X and Y magnetic field values.

        Returns:
            float: Heading angle in degrees.
        """
        x = self.get_mag_x()
        y = self.get_mag_y()
        heading = 180 * atan2(y, x) / pi
        if heading < 0:
            heading += 360
        return heading
