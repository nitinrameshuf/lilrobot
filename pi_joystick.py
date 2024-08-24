import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115

# Create I2C bus instance
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADS1115 instance
ads = ADS1115(i2c)

# Set the gain (adjust this based on your needs)
ads.gain = 1

def read_joystick():
    # Read the X and Y axis values from channels 0 and 1
    x_value = ads.read(0)  # Read from channel 0
    y_value = ads.read(1)  # Read from channel 1
    return x_value, y_value

while True:
    x, y = read_joystick()
    print('Joystick X: {}'.format(x))
    print('Joystick Y: {}'.format(y))
    time.sleep(0.5)
