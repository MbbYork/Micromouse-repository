import uasyncio as asyncio
from machine import Pin, PWM, SoftI2C
import time
import math
from lsm303d import LSM303D
from VL53 import VL53L0X as Sensor

# Global Variables
running = True

# Encoder & Wheel Details
wheel_diameter_mm = 40  # Wheel diameter in mm
ticks_per_revolution = 300  # Number of encoder ticks per revolution
mm_per_tick = math.pi * wheel_diameter_mm / ticks_per_revolution

# Odometry variables
left_count = 0
right_count = 0

# Encoder Setup
encoder_left_A = Pin(12, Pin.IN, Pin.PULL_UP)
encoder_left_B = Pin(13, Pin.IN, Pin.PULL_UP)
encoder_right_A = Pin(14, Pin.IN, Pin.PULL_UP)
encoder_right_B = Pin(15, Pin.IN, Pin.PULL_UP)

# Encoder ISR (Interrupt Service Routine) for left encoder
def update_left_encoder(pin):
    global left_count
    print("Encoder L")
    # Update the encoder count in the ISR
    if encoder_left_B.value() == 0:
        left_count += 1  # Clockwise
    else:
        left_count -= 1  # Counterclockwise

# Encoder ISR (Interrupt Service Routine) for right encoder
def update_right_encoder(pin):
    global right_count
    print("Encoder R")
    # Update the encoder count in the ISR
    if encoder_right_B.value() == 0:
        right_count += 1  # Clockwise
    else:
        right_count -= 1  # Counterclockwise

# Attaches interrupts to the encoder A pins
encoder_left_A.irq(trigger=Pin.IRQ_RISING, handler=update_left_encoder)
encoder_right_A.irq(trigger=Pin.IRQ_RISING, handler=update_right_encoder)

# Motor Control Setup
motor_left_pwm = PWM(Pin(11, Pin.OUT), freq=50000, duty_u16=0)
motor_right_pwm = PWM(Pin(6, Pin.OUT), freq=50000, duty_u16=0)
motor_left_forward = Pin(10, Pin.OUT)
motor_left_backward = Pin(9, Pin.OUT)
motor_right_forward = Pin(7, Pin.OUT)
motor_right_backward = Pin(8, Pin.OUT)

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
course_correction_pid = PID(0.8, 0.01, 0.25, 0)
forward_pid = PID(2.0, 0.01, 0.01, 0)

# PID setpoint and initial dt definitions
forward_pid.setpoint = 50
last_time = time.time()
base_pwm = 17000

async def pid_drive(target_left_speed, target_right_speed):
    global left_count, right_count, current_direction, last_time, base_pwm

    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Ensure dt is not zero
        if dt == 0:
            dt = 0.01  # minimum value to prevent division by zero error
        
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
        
        # Calculate course error using side sensors
        front_distance = max(0, min(frontSensor.read(), 200))
        left_distance = max(0, min(leftSensor.read(), 1000))
        right_distance = max(0, min(rightSensor.read(), 1000))
        course_error = left_distance - right_distance
        front_adj = (front_distance/200)

        # Adjust PWM using heading correction
        pwm_course_correct = course_correction_pid.calculate(course_error, dt)*2
        
        pwm_course_correct = max(-5000, min(5000, int(pwm_course_correct)))

        pwm_left = int(base_pwm*front_adj) + pwm_course_correct
        pwm_right = int(base_pwm*front_adj) - pwm_course_correct
        
        if front_distance<50 and left_distance<50 and right_distance<50:
            print("Dead end detected. Turning around")
            robot.state = "stop"
            await asyncio.sleep(1)
            robot.state = "left"
            await asyncio.sleep(1)
            robot.state = "stop"
        
        if pwm_left > 0:
            motor_left_forward.value(1)
            motor_left_backward.value(0)
        else:
            motor_left_forward.value(0)
            motor_left_backward.value(1)
        if pwm_right > 0:
            motor_right_forward.value(1)
            motor_right_backward.value(0)
        else:
            motor_right_forward.value(0)
            motor_right_backward.value(1)
            
        motor_left_pwm.duty_u16(abs(pwm_left))
        motor_right_pwm.duty_u16(abs(pwm_right))
        
        # Debug for Motor Status and PWM values
        print(f"Left PWM: {pwm_left}, Right PWM: {pwm_right}")
        print(f"Left Motor Status: FWD: {motor_left_forward.value()}, BWD: {motor_left_backward.value()}")
        print(f"Right Motor Status: FWD: {motor_right_forward.value()}, BWD: {motor_right_backward.value()}")
        
        # Distance Debugging
        left_distance_mm = left_count * mm_per_tick
        right_distance_mm = right_count * mm_per_tick
        print(f"Left Distance: {left_count:.2f} mm, Right Distance: {right_distance_mm:.2f} mm")
        
        return running
        await asyncio.sleep(0.01)  # Yield control to other tasks

class Robot:
    def __init__(self, frontSensor, leftSensor, rightSensor):
        # Initialize robot state, motors, sensors, etc.
        self.state = "forward"  # Initial state
        self.motor_left_pwm = 10000
        self.motor_right_pwm = 10000
        self.front_range = frontSensor.read
        self.left_range = leftSensor.read
        self.right_range = rightSensor.read

    async def run(self):
        print("running robot")
        while running:
            distance_front = max(0, min(self.front_range(), 200))
            distance_left = max(0, min(self.left_range(), 300))
            distance_right = max(0, min(self.right_range(), 300))
            print(f"Distances - Front:{distance_front}, Left:{distance_left}, Right:{distance_right}")
            self.update_direction(distance_front,distance_left,distance_right)
            await self.move_robot()
            await asyncio.sleep(0.02)  # Prevent busy-waiting
            
    async def delay(func):
        await asyncio.sleep(10)
        self.state="stop"

    def update_direction(self,front,left,right):
        threshold = 50  # Distance threshold for stopping (mm)
        #self.state = "stop" if front < threshold else "forward"

    async def move_robot(self):
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
            print("Stopping")
            pass

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
    motor_right_forward.value(0)
    motor_right_backward.value(0)
    motor_left_forward.value(0)
    motor_left_backward.value(0)
    robot.state = "stop"
    pid_drive(0,0)
    print("Program terminated.")
