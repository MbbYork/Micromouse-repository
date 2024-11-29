from machine import Pin
import utime
import asyncio

LED = Pin(1,Pin.OUT,Pin.PULL_UP)
trigger = Pin(14, Pin.OUT)
echo = Pin(15, Pin.IN)
def ultra():
   trigger.low()
   utime.sleep_us(2)
   trigger.high()
   utime.sleep_us(5)
   trigger.low()
   while echo.value() == 0:
       signaloff = utime.ticks_us()
   while echo.value() == 1:
       signalon = utime.ticks_us()
   timepassed = signalon - signaloff
   distance = (timepassed * 0.0343) / 2
   if distance >= 5:
       print("The distance from object is ",distance,"cm")
       LED.low()
   else:
       print("Stop robot",distance)
       #stop_event = new Event()
       #stop_event.is_set()
       LED.high()
      
def sensordata2():    
while True:
   ultra()
   utime.sleep(2)
   ultra()
   utime.sleep(2)
