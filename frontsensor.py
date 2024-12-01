from machine import Pin
import utime
import asyncio

LED = Pin(1,Pin.OUT,Pin.PULL_UP)
send = Pin(14, Pin.OUT) 
receive = Pin(15, Pin.IN) 
def sensor():
   send.low()
   utime.sleep_us(2)
   send.high()
   utime.sleep_us(5)
   send.low()
   while receive.value() == 0:
       signaloff = utime.ticks_us()
   while receive.value() == 1:
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
   sensor()
   utime.sleep(2)
   sensor()
   utime.sleep(2)
