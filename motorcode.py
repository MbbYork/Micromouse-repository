import uasyncio as asyncio
from machine import Pin, PWM, SoftI2C
import time
import math
from lsm303d import LSM303D
from VL6180 import Sensor

# Global Variables
current_direction = ""
new_direction = ""
motor_pwm = 10000  # Example PWM speed, can be adjusted
running = True

# Encoder & Wheel Details
wheel_diameter_mm = 40  # Wheel diameter in mm
ticks_per_revolution = 300  # Number of encoder ticks per revolution
mm_per_tick = math.pi * wheel_diameter_mm / ticks_per_revolution

# Odometry variables
left_count = 0
right_count = 0

# Encoder Setup
encoder_left_A = Pin(18, Pin.IN, Pin.PULL_UP)
encoder_left_B = Pin(19, Pin.IN, Pin.PULL_UP)
encoder_right_A = Pin(20, Pin.IN, Pin.PULL_UP)
encoder_right_B = Pin(21, Pin.IN, Pin.PULL_UP)

# Encoder ISR (Interrupt Service Routine) for left encoder
def update_left_encoder(pin):
    global left_count
    # Update the encoder count in the ISR
    if encoder_left_B.value() == 0:
        left_count += 1  # Clockwise
    else:
        left_count -= 1  # Counterclockwise

# Encoder ISR (Interrupt Service Routine) for right encoder
def update_right_encoder(pin):
    global right_count
    # Update the encoder count in the ISR
    if encoder_right_B.value() == 0:
        right_count += 1  # Clockwise
    else:
        right_count -= 1  # Counterclockwise

# Attaches interrupts to the encoder A pins
encoder_left_A.irq(trigger=Pin.IRQ_RISING, handler=update_left_encoder)
encoder_right_A.irq(trigger=Pin.IRQ_RISING, handler=update_right_encoder)

# Motor Control Setup
motor_left_pwm = PWM(Pin(6, Pin.OUT), freq=1000, duty_u16=0)
motor_right_pwm = PWM(Pin(11, Pin.OUT), freq=1000, duty_u16=0)
motor_left_forward = Pin(8, Pin.OUT)
motor_left_backward = Pin(7, Pin.OUT)
motor_right_forward = Pin(9, Pin.OUT)
motor_right_backward = Pin(10, Pin.OUT)

# Accelerometer I2C bus setup
sda = Pin(26)
scl = Pin(27)
#accel = LSM303D(sda_pin=sda,scl_pin=scl)

# PID class definition
class PID:
    def __init__(self, Kp, Ki, Kd, setpoint):
        self.Kp = Kp  # Proportional
        self.Ki = Ki  # Integral
        self.Kd = Kd  # Derivative
        self.setpoint = setpoint
        
        self.prev_err = 0
        self.integral = 0
    
    def calculate(self, measured_value, dt):
        err = self.setpoint - measured_value
        P = self.Kp * err
        self.integral += err * dt
        I = self.Ki * self.integral
        derivative = (err - self.prev_err) / dt
        D = self.Kd * derivative
        self.prev_err = err
        return P + I + D

# Initialize PID controllers for each motor and heading
motor_pid_left = PID(1.0, 0.01, 0.1, 0)
motor_pid_right = PID(1.0, 0.01, 0.1, 0)
heading_pid = PID(1.0, 0.01, 0.1, 0)

async def pid_drive(target_left_speed, target_right_speed):
    global left_count, right_count, current_direction
    
    motor_pid_left.setpoint = target_left_speed
    motor_pid_right.setpoint = target_right_speed

    last_time = time.time()

    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Ensure dt is not zero
        if dt == 0:
            dt = 0.001  # minimum value to prevent division by zero error
        
        # Get accelerometer heading
        #heading = accel.get_heading()
        """
         # Calibrates heading to be within -180 to 180 degrees
        if heading_error > 180:
            heading_error -= 360
        elif heading_error < -180:
            heading_error += 360
        """
        # Calculate heading correction
        #heading_correction = heading_pid.calculate(heading_error, dt)

        # Calculate current speeds from encoders
        current_left_speed = left_count
        current_right_speed = right_count
        left_count = 0 # Resets counters after reading
        right_count = 0

        # Adjust PWM using heading correction
        pwm_left = motor_pid_left.calculate(current_left_speed, dt) #- heading_correction
        pwm_right = motor_pid_right.calculate(current_right_speed, dt) #+ heading_correction

        pwm_left = max(-65535, min(65535, int(pwm_left)))
        pwm_right = max(-65535, min(65535, int(pwm_right)))
        
        if pwm_left>0:
             # Wall Following
            wall_distance = 50 # Target distance
            current_wall_distance = rightSensor.range()
            wall_error = current_wall_distance - wall_distance
            pwm_right_adjustment = wall_error * 100  # Proportional adjustment

            pwm_right += pwm_right_adjustment

        motor_left_pwm.duty_u16(abs(pwm_left))
        motor_right_pwm.duty_u16(abs(pwm_right))
        if pwm_left >= 0:
            motor_left_forward.value(1)
            motor_left_backward.value(0)
        else:
            motor_left_forward.value(0)
            motor_left_backward.value(1)
        if pwm_right >= 0:
            motor_right_forward.value(1)
            motor_right_backward.value(0)
        else:
            motor_right_forward.value(0)
            motor_right_backward.value(1)
        
        # Debug for Motor Status and PWM values
        print(f"Left PWM: {pwm_left}, Right PWM: {pwm_right}")
        print(f"Left Motor Status: FWD: {motor_left_forward.value()}, BWD: {motor_left_backward.value()}")
        print(f"Right Motor Status: FWD: {motor_right_forward.value()}, BWD: {motor_right_backward.value()}")
        
        # Distance Debugging
        left_distance_mm = left_count * mm_per_tick
        right_distance_mm = right_count * mm_per_tick
        print(f"Left Distance: {left_count:.2f} mm, Right Distance: {right_distance_mm:.2f} mm")
        
        return running
        await asyncio.sleep(0.05)  # Yield control to other tasks

class Robot:
    def __init__(self, frontSensor, leftSensor, rightSensor):
        # Initialize robot state, motors, sensors, etc.
        self.state = "forward"  # Initial state
        self.motor_left_pwm = 10000
        self.motor_right_pwm = 10000
        self.front_range = frontSensor.range
        self.left_range = leftSensor.range
        self.right_range = rightSensor.range

    async def run(self):
        print("running robot")
        while running:
            distance_front = self.front_range()
            distance_left = self.left_range()
            distance_right = self.right_range()
            print(f"Distances - Front:{distance_front}, Left:{distance_left}, Right:{distance_right}")
            self.update_direction(distance_front,distance_left,distance_right)
            await self.move_robot()
            await asyncio.sleep(0.1)  # Prevent busy-waiting

    def update_direction(self,front,left,right):
        threshold = 50  # Distance threshold for stopping (mm)
        self.state = "stop" if front < threshold else "forward"

    async def move_robot(self):
        print("moving robot")
        if self.state == "forward":
            await pid_drive(self.motor_left_pwm,self.motor_right_pwm)
            print("Moving forward")
        elif self.state == "backward":
            await pid_drive(-self.motor_left_pwm,-self.motor_right_pwm)
            print("Moving backward")
        elif self.state == "right":
            await pid_drive(-self.motor_left_pwm,self.motor_right_pwm)
            print("Moving right")
        elif self.state == "left":
            await pid_drive(self.motor_left_pwm,-self.motor_right_pwm)
            print("Moving left")
        elif self.state == "stop":
            await pid_drive(0,0)
            motor_right_forward.value(0)
            motor_right_backward.value(0)
            print("Stopping")
        else:
            await pid_drive(0,0)
            motor_right_forward.value(0)
            motor_right_backward.value(0)
            print("Stopping due to invalid state")

#---------Main Code------------
# Sensor setup
front_i2c = SoftI2C(sda=Pin(0), scl=Pin(1), freq=50000)
left_i2c = SoftI2C(sda=Pin(2), scl=Pin(3), freq=50000)
right_i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=50000)
frontSensor = Sensor(front_i2c)
leftSensor = Sensor(left_i2c)
rightSensor = Sensor(right_i2c)
robot = Robot(frontSensor, leftSensor, rightSensor)

async def main():
    await robot.run()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    robot.running = False
    robot.motor_left_pwm.duty_u16(0)
    robot.motor_right_pwm.duty_u16(0)
    print("Program terminated.")
