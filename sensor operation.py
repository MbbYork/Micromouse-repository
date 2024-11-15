from machine import pin
import utime

trigger = Pin(3,Pin.OUT)
echo = Pin(2,Pin.IN)
   
def ultra():
      #this pulls the trigger low and pauses for 2ms
      trigger.low()
      utime.sleep_us(2)
      
      #This pulls the pull trigger high for 5ms before pulling the trigger low
      tigger.high()
      utime.sleep_us(5)
      trigger.low()
      
      #while loop to check the echo pin
      while echo.value() == 0:
       signaloff = utime.ticks_us()
       
      #while loop checks if the echo has been received
      while echo.value() == 1:
       signalon = utime.ticks_us()
           
       # variable which stores data that takes the total time between pulse being transmitted and received
      timepassed = signalon -signaloff
       
       #variable distance stores the distance value calculated from the equation
      distance = (timepassed * 0.0343)/2
        #message is printed to Python shell
      print("Distance from the option is ",distance,"cm")
      
while(true):
   ultra()
   utime.sleep(1)
