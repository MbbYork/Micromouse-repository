import uasyncio as asyncio
from machine import Pin, PWM, SoftI2C
import time
import math
from VL53 import VL53L0X as Sensor

# Constants
WHEEL_DIAMETER_MM = 40  # Wheel diameter in mm
TICKS_PER_REVOLUTION = 300  # Encoder ticks per revolution
MM_PER_TICK = math.pi * WHEEL_DIAMETER_MM / TICKS_PER_REVOLUTION
BASE_PWM = 19000
STOP_DISTANCE_THRESHOLD = 50  # Minimum safe distance to stop (mm)
TURN_DURATION_90_DEGREES = 0.3 # Duration to complete a 90-degree turn (seconds)

# Encoder variables
left_count = 0
right_count = 0

# Motor control pins and setup
motor_pins = {
    "left_forward": Pin(10, Pin.OUT),
    "left_backward": Pin(9, Pin.OUT),
    "right_forward": Pin(7, Pin.OUT),
    "right_backward": Pin(8, Pin.OUT),
}

motor_pwm = {
    "left": PWM(Pin(11, Pin.OUT), freq=50000, duty_u16=0),
    "right": PWM(Pin(6, Pin.OUT), freq=50000, duty_u16=0),
}

# Encoder setup
encoder_pins = {
    "left_A": Pin(12, Pin.IN, Pin.PULL_UP),
    "left_B": Pin(13, Pin.IN, Pin.PULL_UP),
    "right_A": Pin(14, Pin.IN, Pin.PULL_UP),
    "right_B": Pin(15, Pin.IN, Pin.PULL_UP),
}

def update_encoder(pin, count_var):
    global left_count, right_count
    count = left_count if count_var == "left" else right_count
    if encoder_pins[f"{count_var}_B"].value() == 0:
        count += 1  # Clockwise
    else:
        count -= 1  # Counterclockwise
    if count_var == "left":
        left_count = count
    else:
        right_count = count

encoder_pins["left_A"].irq(trigger=Pin.IRQ_RISING, handler=lambda pin: update_encoder(pin, "left"))
encoder_pins["right_A"].irq(trigger=Pin.IRQ_RISING, handler=lambda pin: update_encoder(pin, "right"))

# PID controller class
class PID:
    def __init__(self, Kp, Ki, Kd, setpoint):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.prev_err = 0
        self.integral = 0

    def calculate(self, measured_value, dt):
        err = self.setpoint - measured_value
        self.integral += err * dt
        derivative = (err - self.prev_err) / dt
        self.prev_err = err
        return self.Kp * err + self.Ki * self.integral + self.Kd * derivative

# Robot class
class Robot:
    def __init__(self, front_sensor, left_sensor, right_sensor):
        self.front_sensor = front_sensor
        self.left_sensor = left_sensor
        self.right_sensor = right_sensor
        self.state = "stop"
        self.pids = {
            "course": PID(1.0, 0.01, 0.25, 0),
            "forward": PID(2.0, 0.01, 0.01, 0),
        }

    async def forward(self):
        global left_count, right_count
        last_time = time.time()
        start_time = time.time()
        while time.time() - start_time < 1 and self.state != "stop":
            current_time = time.time()
            dt = max(current_time - last_time, 0.01)
            last_time = current_time

            # Calculate encoder speeds
            left_speed = left_count
            right_speed = right_count
            left_count = 0
            right_count = 0

            # Sensor readings
            front_distance = self.front_sensor.read()
            left_distance = self.left_sensor.read()
            right_distance = self.right_sensor.read()

            # Debug prints
            print(f"Front Distance: {front_distance} mm, Left Distance: {left_distance} mm, Right Distance: {right_distance} mm")
            print(f"Left Speed: {left_speed}, Right Speed: {right_speed}")

            # Speed adjustment based on proximity to obstacle
            if front_distance < STOP_DISTANCE_THRESHOLD * 3:
                # Scale PWM based on front_distance
                speed_scale = max(0.1, front_distance / (STOP_DISTANCE_THRESHOLD * 3))
                adjusted_pwm = int(BASE_PWM * speed_scale)
                print(f"Adjusting speed. Scale: {speed_scale:.2f}, PWM: {adjusted_pwm}")
            else:
                adjusted_pwm = BASE_PWM

            # Dead-end handling
            if front_distance < STOP_DISTANCE_THRESHOLD and left_distance < STOP_DISTANCE_THRESHOLD and right_distance < STOP_DISTANCE_THRESHOLD:
                print("Dead end detected. Turning around.")
                await self.turn_around()
                continue

            # Calculate course correction
            course_error = left_distance - right_distance
            pwm_course_correct = self.pids["course"].calculate(course_error, dt)
            pwm_course_correct = max(-5000, min(5000, int(pwm_course_correct)))

            # Adjust motor speeds
            pwm_left = adjusted_pwm + pwm_course_correct
            pwm_right = adjusted_pwm - pwm_course_correct

            self.set_motor_pwm(pwm_left, pwm_right)

            # Debug prints for PWM
            print(f"PWM Left: {pwm_left}, PWM Right: {pwm_right}")

            await asyncio.sleep(0.01)

    async def turn_around(self):
        print("Turning around.")
        self.set_motor_pwm(-BASE_PWM, BASE_PWM)  # Simple left turn
        await asyncio.sleep(0.6)  # Adjust duration for a 180-degree turn
        self.state = "forward"

    async def turn_left(self):
        print("Turning left 90 degrees")
        self.set_motor_pwm(-BASE_PWM, BASE_PWM)
        await asyncio.sleep(TURN_DURATION_90_DEGREES)
        self.set_motor_pwm(0, 0)

    async def turn_right(self):
        print("Turning right 90 degrees")
        self.set_motor_pwm(BASE_PWM, -BASE_PWM)
        await asyncio.sleep(TURN_DURATION_90_DEGREES)
        self.set_motor_pwm(0, 0)

    def set_motor_pwm(self, left_pwm, right_pwm):
        # Update motor direction and PWM
        motor_pins["left_forward"].value(left_pwm > 0)
        motor_pins["left_backward"].value(left_pwm < 0)
        motor_pins["right_forward"].value(right_pwm > 0)
        motor_pins["right_backward"].value(right_pwm < 0)

        motor_pwm["left"].duty_u16(abs(left_pwm))
        motor_pwm["right"].duty_u16(abs(right_pwm))

        # Debug prints for motor status
        print(f"Left Motor: Forward={motor_pins['left_forward'].value()}, Backward={motor_pins['left_backward'].value()}")
        print(f"Right Motor: Forward={motor_pins['right_forward'].value()}, Backward={motor_pins['right_backward'].value()}")

    async def drive_instructions(self, instructions):
        for instruction in instructions:
            if instruction == "forward":
                await self.forward()
            elif instruction == "turn_left":
                await self.turn_left()
            elif instruction == "turn_right":
                await self.turn_right()
            else:
                print(f"Unknown instruction: {instruction}")
            await asyncio.sleep(0.5)

# Main function
async def main():
    front_sensor = Sensor(SoftI2C(sda=Pin(0), scl=Pin(1), freq=100000))
    left_sensor = Sensor(SoftI2C(sda=Pin(2), scl=Pin(3), freq=100000))
    right_sensor = Sensor(SoftI2C(sda=Pin(4), scl=Pin(5), freq=100000))

    robot = Robot(front_sensor, left_sensor, right_sensor)
    robot.state = "forward"
    instructions = ["forward","forward","forward","forward","forward","forward","forward","forward","forward","forward"]
    try:
        await robot.drive_instructions(instructions)
    except KeyboardInterrupt:
        robot.state = "stop"
        robot.set_motor_pwm(0, 0)
        print("Program terminated.")

# Run the program
try:
    asyncio.run(main())
except Exception as e:
    print(f"Error: {e}")
