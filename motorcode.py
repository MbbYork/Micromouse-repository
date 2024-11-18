import uasyncio as asyncio
from machine import Pin, PWM
import time, lsm303d

"""
---------Notes for code module---------
Inputs needed for code functionality:
 - new_direction from pathfinding code
 - motor_pwm for speed of movement

Remember to set the input pins (marked with <-----------)
Tune PID when testing
"""

# Global Variables
current_direction = ""
new_direction = ""
motor_pwm = 10000  # Example PWM speed, can be adjusted
running = True

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

# Motor Control Setup
motor_left_pwm = PWM(Pin(0,Pin.OUT), freq=1000, duty_u16=0) # PWM Pin for left motor
motor_right_pwm = PWM(Pin(5,Pin.OUT), freq=1000, duty_u16=0) # PWM Pin for right motor
motor_left_forward = Pin(1,Pin.OUT)
motor_left_backward = Pin(2,Pin.OUT)
motor_right_forward = Pin(3,Pin.OUT)
motor_right_backward = Pin(4,Pin.OUT)

# Accelerometer setup
lsm = LSM303D()

# Encoder Variables
left_count = 0
right_count = 0

# Initialize PID controllers for each motor
motor_pid_left = PID(2.0, 0.1, 0.01, 0)
motor_pid_right = PID(2.0, 0.1, 0.01, 0)

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
        
        current_left_speed = left_count
        current_right_speed = right_count
        left_count = 0
        right_count = 0

        pwm_left = motor_pid_left.calculate(current_left_speed, dt)
        pwm_right = motor_pid_right.calculate(current_right_speed, dt)

        # PWM values clamped between 0 and 65535 for duty cycle
        pwm_left = max(-65535, min(65535, int(pwm_left)))
        pwm_right = max(-65535, min(65535, int(pwm_right)))

        motor_left_pwm.duty_u16(abs(pwm_left))
        motor_right_pwm.duty_u16(abs(pwm_right))
        if pwm_left >= 0:
            motor_left_forward.value(1)
            motor_left_backward.value(0)
        elif pwm_left < 0:
            motor_left_forward.value(0)
            motor_left_backward.value(1)
        if pwm_right >= 0:
            motor_right_forward.value(1)
            motor_right_backward.value(0)
        elif pwm_right < 0:
            motor_right_forward.value(0)
            motor_right_backward.value(1)
            
        print(f"current pwm - left: {pwm_left}, right: {pwm_right}\nLeft Motor status: fwd: {motor_left_forward.value()}, bwd: {motor_left_backward.value()}\nRight Motor status: fwd: {motor_right_forward.value()}, bwd: {motor_right_backward.value()}")

        # Stop the motors after completing a turn
        if current_direction in ["left", "right"]:
            if abs(left_count) >= abs(motor_pid_left.setpoint) and abs(right_count) >= abs(motor_pid_right.setpoint):
                motor_left_pwm.duty_u16(0)
                motor_right_pwm.duty_u16(0)
                break

        await asyncio.sleep(0.05)  # Yield control to other tasks

async def direction_listen():
    global current_direction, new_direction
    while running:
        print("Direction listen event")
        if current_direction != new_direction:
            if new_direction in ["forward", "backward", "left", "right"]:
                current_direction = new_direction
                print(f"Direction updated to: {current_direction}")
            elif new_direction == "stop":
                current_direction = "stop"
                motor_left_pwm.duty_u16(0)
                motor_right_pwm.duty_u16(0)
                print("Motors stopped")
            else:
                print("Invalid direction input detected")
        await asyncio.sleep(0.05)  # Yield control to other tasks
        
async def manual_input():
    global new_direction
    user_input = input("Enter new direction (forward, backward, left, right, stop): ")
    if user_input in ["forward", "backward", "left", "right", "stop"]:
        new_direction = user_input
    else:
        print("Invalid direction. Try again.")
    await asyncio.sleep(0.1)  # Yield control to keep the program responsive

async def update_drive(pwm):
    global current_direction
    while running:
        if current_direction == "forward":
            await pid_drive(pwm, pwm)
        elif current_direction == "backward":
            await pid_drive(-pwm, -pwm)
        elif current_direction == "left":
            await pid_drive(-pwm, pwm)
        elif current_direction == "right":
            await pid_drive(pwm, -pwm)
        await asyncio.sleep(0.1)  # Slight delay to reduce CPU load

def updateAccel():
    print(lsm.accelerometer(), lsm.magnetometer())

# Main function to start all tasks
async def main():
    print("Boot successful")
    drive_task = asyncio.create_task(update_drive(motor_pwm))
    listen_task = asyncio.create_task(direction_listen())
    input_task = asyncio.create_task(manual_input())
    accel_task = asyncio.create_task(updateAccel())
    if running:
        await asyncio.gather(drive_task, listen_task,accel_task)

# Run the main function using asyncio event loop
try:
    asyncio.run(main())
except KeyboardInterrupt:
    running = False
    motor_left_pwm.duty_u16(0)
    motor_right_pwm.duty_u16(0)
    print("Program terminated.")
