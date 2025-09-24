import time
import RPi.GPIO as GPIO  
import cv2
import numpy as np
import os

import sensors
import conveyorbelt
import img_processing
import classification
from stepper_motor import StepperMotorController 
import camera

from feeding_system import feedingsystem_start, feedingsystem_stop, feedingsystem_restart
from conveyorbelt import conveyorbelt_start, conveyorbelt_stop, conveyorbelt_restart_1
from rpi_ws281x import PixelStrip, Color


"""
————————————————————————————————————————————————————————————————————————————————————————————————————————


Control Flow
Step 1: Automatically starts upon power-on: feeder motor, conveyor belt motor, ring light, sensor →
Step 2: Object to be inspected is fed in →
Step 3: Sensor detects the object →
Step 4: Feeder and conveyor belt stop →
Step 5: Image capture and processing →
Step 6: Classification and result determination →
Step 7: Stepper motor starts (resets after 3 seconds) →
Step 8: Main conveyor belt starts (stops after 1 second) →
Step 9: Feeder and conveyor belt systems restart →
Step 10: Return to step 2
——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""

RING_LIGHT_PIN = 18  
LED_COUNT = 16
LED_FREQ_HZ = 800000
LED_DMA = 10             
LED_INVERT = False        
LED_BRIGHTNESS = 10



class RingLight:
    def __init__(self, count=LED_COUNT, pin=RING_LIGHT_PIN, brightness=LED_BRIGHTNESS):
        self.led_count = count
        self.brightness = brightness
        
        # stand by
        time.sleep(1)
        self.strip = PixelStrip(count, pin, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
        self.strip.begi
        self.strip.setBrightness(self.brightness)
        self.strip.show()  
    
    def turn_on(self, color=Color(255, 255, 255)):
        """All lamp beads light up the specified color, the default is white"""
      
        time.sleep(0.5)
        for i in range(self.led_count):
            self.strip.setPixelColor(i, color)
        self.strip.show()
        print("Ring light turned on.")
        
    def turn_off(self):
        """All lamp beads are turned off"""
        for i in range(self.led_count):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()
        print("Ring light turned off.")
        



def main():
    
    time.sleep(2) 
    GPIO.setmode(GPIO.BCM)
    
    
    # Initialize 
    sensor = sensors.InfraredSensor()
    ring_light = RingLight()
    
    roi = (380, 280, 1280, 200)
    pixel_to_mm = 0.075


    
    try:
        # step 1: Start the conveyor belt, ring light, and the sensor GPIO has been initialized
        feedingsystem_start()
        conveyorbelt_start()
    
        ring_light.turn_on()
        
        #
        while True:
            print("等待检测到物体...")
            
            # Step 2 & 3 & 4: Loop to determine if the sensor detects an object, and if so, stop the conveyor and feed.
            while True:
                if sensor.is_object_detected():
                    print("检测到物体，停止进料和传送带")
                    conveyorbelt_stop()
                    feedingsystem_stop()
                    break
                else:
                    conveyorbelt_start()
                    feedingsystem_start()
                time.sleep(0.1)
        
            # step 5： Take a picture and save it 
            image_path = camera.capture_image()
            print(f"Image captured and saved to {image_path}")

            # step 6： Read the image and detect 
            result = img_processing.img_recog(image_path, roi, pixel_to_mm)
            print('Detection result:')
            print(f"Part type: {result['part_type']}")
            print(f"Length: {result['length_px']:.1f} px / {result['length_mm']:.2f} mm")
            print(f"Diameter: {result['diameter_px']:.1f} px / {result['diameter_mm']:.2f} mm")
            print(f"Angle: {result['angle']:.1f} degrees")
            print(f"Aspect ratio: {result['aspect_ratio']:.2f}")

            #  Classify 
            model = classification.classify_model(result)
            print(f'Matched Model: {model}')

            # step 7： Control the stepper motor to rotate to the corresponding angle and reset 
            motor = StepperMotorController()
            motor.rotate(model) 
         
            # step 8
            # Start only the long conveyor belt and stop it after 1 second
            conveyorbelt._start_long()  
            time.sleep(1.5)
            conveyorbelt._stop_long()
            
            time.sleep(3)
            motor.reset(model) 
            
            # Then start the feeding and conveyor belt at the same time to start the next round of recognition
            feedingsystem_start()
            conveyorbelt_start()
            
            # step 10 loop back and wait for sensor detection..
            
            
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    main()
