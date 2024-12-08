import frontsensor
import motor_driver

class Robot:
    def __init__(self):
        self.state = "forward"  # Initial state
        self.motor_left_pwm = 1000
        self.motor_right_pwm = 1000
        self.sensor = frontsensor.sensor

    def run(self):
        print("running robot")
        while True:
            #distance = self.sensor()
            self.update_direction(distance)
            self.move_robot()

    def update_direction(self, distance):
        print("updating sensors")
        threshold = 5  # Distance threshold for stopping (cm)
        if distance < threshold:
            self.state = "stop"
        else:
            self.state = "forward" 

    def move_robot(self):
        print("moving robot")
        # Implement state-based movement logic based on robot state
        if self.state == "forward":
            pid_drive(self.motor_left_pwm,self.motor_right_pwm)
        elif self.state == "backward":
            pid_drive(-self.motor_left_pwm,-self.motor_right_pwm)
        elif self.state == "right":
            pid_drive(-self.motor_left_pwm,self.motor_right_pwm)
        elif self.state == "left":
            pid_drive(self.motor_left_pwm,-self.motor_right_pwm)
        elif self.state == "stop":
            pid_drive(0,0)
    
#---------Main Code------------
#if __name__ == "__main__":
robot = Robot()
print("test")
robot.run()
