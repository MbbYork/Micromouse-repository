import uasyncio as asyncio
from machine import Pin, PWM, SoftI2C
import time
import math
from VL53 import VL53L0X as Sensor
from collections import deque

# Constants
WHEEL_DIAMETER_MM = 40  # Wheel diameter in mm
TICKS_PER_REVOLUTION = 300  # Encoder ticks per revolution
MM_PER_TICK = math.pi * WHEEL_DIAMETER_MM / TICKS_PER_REVOLUTION
BASE_PWM = 17000
STOP_DISTANCE_THRESHOLD = 60  # Minimum safe distance to stop (mm)
TURN_DURATION_90_DEGREES = 0.5  # Duration to complete a 90-degree turn (seconds)

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

# Constants
STOP_DISTANCE_THRESHOLD = 50  # Minimum safe distance to stop (mm)
TURN_DURATION_90_DEGREES = 0.4 # Duration to complete a 90-degree turn (seconds)
BASE_PWM = 5000  # Base PWM value for motor speed

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
    def __init__(self, front_sensor, left_sensor, right_sensor, start=(0, 0)):
        self.front_sensor = front_sensor
        self.left_sensor = left_sensor
        self.right_sensor = right_sensor
        self.start = start
        self.state = "stop"
        self.map = {}  # To store the grid map
        self.pids = {
            "course": PID(1.0, 0.01, 0.25, 0),
            "forward": PID(2.0, 0.01, 0.01, 0),
        }

    async def scan_environment(self):
        # Scan and create a map of the environment
        while True:
            front_distance = self.front_sensor.get_distance()
            left_distance = self.left_sensor.get_distance()
            right_distance = self.right_sensor.get_distance()

            self.map[(0, 0)] = {
                "front": front_distance,
                "left": left_distance,
                "right": right_distance
            }

            await asyncio.sleep(0.1)  # Scan every 100ms

    async def forward(self):
        last_time, start_time = time.time(), time.time()
        while time.time() - start_time < 1 or self.state != "stop":
            current_time = time.time()
            dt = max(current_time - last_time, 0.01)
            last_time = current_time

            # Speed adjustment based on proximity to obstacle
            front_distance = self.map[(0, 0)]["front"]
            if front_distance < STOP_DISTANCE_THRESHOLD * 2:
                speed_scale = max(0.1, front_distance / (STOP_DISTANCE_THRESHOLD * 2))
                adjusted_pwm = int(BASE_PWM * speed_scale)
                print(f"Adjusting speed. Scale: {speed_scale:.2f}, PWM: {adjusted_pwm}")
            else:
                adjusted_pwm = BASE_PWM

            # Dead-end handling
            if front_distance < STOP_DISTANCE_THRESHOLD and self.map[(0, -1)]["front"] < STOP_DISTANCE_THRESHOLD and self.map[(-1, 0)]["front"] < STOP_DISTANCE_THRESHOLD:
                print("Dead end detected. Turning around.")
                await self.turn_around()
                continue

            # Calculate course correction
            left_distance = self.map[(0, -1)]["left"]
            right_distance = self.map[(0, 1)]["right"]
            course_error = left_distance - right_distance
            pwm_course_correct = self.pids["course"].calculate(course_error, dt)
            pwm_course_correct = max(-5000, min(5000, int(pwm_course_correct)))

            # Adjust motor speeds
            pwm_left = adjusted_pwm + pwm_course_correct
            pwm_right = adjusted_pwm - pwm_course_correct

            self.set_motor_pwm(pwm_left, pwm_right)

            await asyncio.sleep(0.01)

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

    async def find_path(self, start, goal):
        # BFS algorithm for pathfinding
        queue = deque([start],(13*13))
        visited = set()
        parent = {start: None}

        while queue:
            current = queue.popleft()

            if current == goal:
                path = []
                while current:
                    path.append(current)
                    current = parent[current]
                return path[::-1]  # Return reversed path

            x, y = current
            visited.add(current)

            # Possible moves: forward, left, right
            moves = [(0, -1), (-1, 0), (0, 1)]  # Correspond to (left, down, right)
            for move in moves:
                new_pos = (x + move[0], y + move[1])
                if new_pos not in visited and self.map.get(new_pos) and self.map[new_pos]["front"] > STOP_DISTANCE_THRESHOLD:
                    queue.append(new_pos)
                    parent[new_pos] = current
            print(queue[0])

    async def navigate_to_goal(self, goal):
        path = await self.find_path(self.start, goal)
        
        if path != None:
            print(path)
            for step in path:
                if step == (0, -1):
                    await self.turn_left()
                elif step == (-1, 0):
                    await self.forward()
                elif step == (0, 1):
                    await self.turn_right()
                else:
                    print("Unknown step in path.")

async def main():
    front_sensor = Sensor(SoftI2C(sda=Pin(0), scl=Pin(1), freq=100000))
    left_sensor = Sensor(SoftI2C(sda=Pin(2), scl=Pin(3), freq=100000))
    right_sensor = Sensor(SoftI2C(sda=Pin(4), scl=Pin(5), freq=100000))

    robot = Robot(front_sensor, left_sensor, right_sensor)
    robot.state = "forward"

    # Start scanning environment in parallel
    asyncio.create_task(robot.scan_environment())

    try:
        # Navigate through the maze (example path instructions)
        await robot.navigate_to_goal(goal=(2, 2))
    except KeyboardInterrupt:
        robot.state = "stop"
        self.set_motor_pwm(0, 0)
        print("Program terminated.")

# Run the program
asyncio.run(main())
"""
try:
    asyncio.run(main())
except Exception as e:
    print(f"Error: {e}")
"""
