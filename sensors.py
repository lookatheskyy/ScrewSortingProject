import time
import RPi.GPIO as GPIO  




"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

Infrared sensor function:
Detecting digital high and low levels determines whether an object is detected.

Model: MH-Sensor-series Flying Flash
Typically, a threshold voltage is used to determine whether an object is detected.

GPIO Wiring:
VCC to 3.3V or 5V
GND to Raspberry Pi GND
OUT to Raspberry Pi GPIO input port (BCM number)



——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""



SENSOR_PIN = 16

class InfraredSensor:
    def __init__(self, pin=SENSOR_PIN):
        self.pin = pin   
        self.object_detected = False  

        GPIO.setmode(GPIO.BCM)     
        GPIO.setup(self.pin, GPIO.IN)   

        
        # 监听引脚电平的上升沿或下降沿 (GPIO.BOTH)，防抖时间200ms
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self._sensor_callback, bouncetime=200)

    def _sensor_callback(self, channel):
        """
        The callback function called when the event detection is triggered. The parameter channel is the GPIO pin number of the trigger.
        """
        level = GPIO.input(self.pin)
        # Determine whether there is an object based on the detected level
        # Low level (0) indicates that an object is detected, high level (1) indicates that there is no object
        if level == 0:   # Detected by multimeter: low level indicates the presence of an object
            self.object_detected = True
        else:
            self.object_detected = False

    def is_object_detected(self):
        """
        External query interface, returns the status of whether the object is currently detected
        """
        return self.object_detected

   



if __name__ == "__main__":
    
    sensor = InfraredSensor(SENSOR_PIN)
    try:
        while True:
            if sensor.is_object_detected():
                print("detect objects！")
            else:
                print("no objects")
            time.sleep(0.1)
    except KeyboardInterrupt:
        sensor.cleanup()