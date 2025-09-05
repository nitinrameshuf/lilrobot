import time
import board
import busio
from adafruit_ads1x15.ads1015 import ADS1015, P0, P1, P2, P3
from adafruit_ads1x15.analog_in import AnalogIn

# Setup I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Init ADC
ads = ADS1015(i2c)
ads.gain = 1

# Joystick channels
joy1_x = AnalogIn(ads, P0)
joy1_y = AnalogIn(ads, P1)
joy2_x = AnalogIn(ads, P2)
joy2_y = AnalogIn(ads, P3)

# Read loop
try:
    while True:
        print(f"Joystick 1 -> X: {joy1_x.value}, Y: {joy1_y.value}")
        print(f"Joystick 2 -> X: {joy2_x.value}, Y: {joy2_y.value}")
        print("-" * 50)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped by user.")
