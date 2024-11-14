from gpiozero import Motor,PWMOutputDevice,DigitalInputDevice
from time import sleep,time
import threading

"""
---------Notes for code module---------
Inputs needed for code functionality:
 - new_direction from pathfinding code
 - motor_pwm for speed of movement
 
Remember to set the input pins(marked with <-----------)

Tune PID when testing
"""

current_direction = ""
new_direction = ""
motor_pwm = 0
running = True

# PID class definition
class PID:
    def __init__(self, Kp, Ki, Kd, setpoint):
        self.Kp = Kp # Proportional
        self.Ki = Ki # Integral
        self.Kd = Kd # Derivative
        self.setpoint = setpoint
        
        self.prev_err = 0
        self.integral = 0
    
    def calculate(self, measured_value, dt):
        err = self.setpoint - measured_value
        
        # Proportional gain
        P = self.Kp * err
        
        # Integral gain
        self.integral += err * dt
        I = self.Ki * self.integral
        
        # Derivative gain (d/dt of error)
        derivative = (err-self.prev_err)/dt
        D = self.Kd * derivative
        
        self.prev_err = err
        
        return (P+I+D)
    
#---------------Main Motor code--------------------

# Motor Control Setup
motor_pwm_left = # PWM Pin for left motor <-----------
motor_pwm_right = # PWM Pin for right motor <-----------
motor_left = Motor(motor_pwm_left)
motor_right = Motor(motor_pwm_right)

# Encoder Setup
encoder_left_pin = # encoder left pin placeholder <-----------
encoder_right_pin = # encoder right pin placeholder <-----------
encoder_left = DigitalInputDevice(encoder_left_pin)
encoder_right = DigitalInputDevice(encoder_right_pin)
left_count = 0
right_count = 0

# Encoder callbacks
lock = threading.Lock() # Thread lock for thread safety

def left_encoder_callback():
    global left_count
    with lock:
        left_count += 1

def right_encoder_callback():
    global right_count
    with lock:
        right_count += 1

# Attach callbacks to encoder revolution event
encoder_left.when_activated = left_encoder_callback
encoder_right.when_activated = right_encoder_callback

# Initialising PID object for each motor
motor_pid_left = PID(1.0,0.1,0.01,0)
motor_pid_right = PID(1.0,0.1,0.01,0)

# Motor drive & odometry function
def pid_drive(target_left_speed, target_right_speed):
    global left_count, right_count, current_direction
    
    # Sets PID setpoint
    if current_direction in ["forward", "backward"]:
        motor_pid_left.setpoint = target_left_speed
        motor_pid_right.setpoint = target_right_speed
    elif current_direction == ("left"):
        motor_pid_left.setpoint = -100# Measure how many counts it takes for a 90 degree turn <-----------
        motor_pid_right.setpoint = 100# Measure how many counts it takes for a 90 degree turn <-----------
    elif current_direction == ("right"):
        motor_pid_left.setpoint = 100# Measure how many counts it takes for a 90 degree turn <-----------
        motor_pid_right.setpoint = -100# Measure how many counts it takes for a 90 degree turn <-----------
    
    last_time = time()
    
    while running:
        # Calculates time elapsed
        current_time = time()
        dt = current_time - last_time
        last_time = current_time
        
        # Speed odometry using encoder counts
        current_left_speed = left_count
        current_right_speed = right_count
        
        # PID control outputs
        pwm_left = motor_pid_left.calculate(current_left_speed,dt)
        pwm_right = motor_pid_right.calculate(current_right_speed,dt)
        
        # Set motor speeds using PWM
        motor_left.value = max(-1, min(1, pwm_left))
        motor_right.value = max(-1, min(1, pwm_right))
        
         # Break condition for 90-degree turns
        if current_direction in ["left", "right"]:
            if abs(left_count) >= abs(motor_pid_left.setpoint) and abs(right_count) >= abs(motor_pid_right.setpoint):
                motor_left.value = 0
                motor_right.value = 0
                left_count = 0
                right_count = 0
                break
        
        if current_direction in ["forward", "backward"]:
            left_count = 0
            right_count = 0
        
        sleep(0.05)

# Listen function to detect change in pathfinding input
def direction_listen():
    global current_direction
    global new_direction
    while running:
        if current_direction != new_direction:
            if new_direction in  ["forward","backward","left","right"]:
                current_direction = new_direction
            elif new_direction == "stop":
                motor_left.value = 0
                motor_right.value = 0
            else:
                print("Invalid direction input detected")
        sleep(0.05)
        
# Movement control function
def update_drive(pwm):
    global current_direction
    while running:
        if current_direction == "forward":
            pid_drive(pwm, pwm)  # Move forward
        elif current_direction == "backward":
            pid_drive(-pwm, -pwm) # Move backward 
        elif current_direction == "left":
            pid_drive(-pwm, pwm) # Turn left
        elif current_direction == "right":
            pid_drive(pwm, -pwm)  # Turn right
        sleep(0.05) # Slight delay to reduce cpu load

# Starts new thread for direction listening function
direction_thread = threading.Thread(target=direction_listen)
direction_thread.start()

# Start drive update loop
try:
    update_drive(motor_pwm)
except KeyboardInterrupt:
    running = False