from machine import Pin,PWM
motor_left_pwm = PWM(Pin(6, Pin.OUT), freq=100, duty_u16=32000)
motor_right_pwm = PWM(Pin(11, Pin.OUT), freq=100, duty_u16=32000)
motor_left_forward = Pin(8, Pin.OUT)
motor_left_backward = Pin(7, Pin.OUT)
motor_right_forward = Pin(9, Pin.OUT)
motor_right_backward = Pin(10, Pin.OUT)
try:
    motor_left_forward.value(1)
    motor_right_forward.value(1)
except KeyboardInterrupt:
    motor_left_forward.value(0)
    motor_right_forward.value(0)
