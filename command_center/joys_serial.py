import time
import board
import busio
import serial
from adafruit_ads1x15.ads1015 import ADS1015, P0, P1, P2, P3
from adafruit_ads1x15.analog_in import AnalogIn

# Setup I2C for ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1015(i2c)
ads.gain = 1

# Joystick channels
joy1_x = AnalogIn(ads, P0)
joy1_y = AnalogIn(ads, P1)
joy2_x = AnalogIn(ads, P2)
joy2_y = AnalogIn(ads, P3)

# Setup Serial to SparkFun Artemis
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Change port if needed
time.sleep(2)  # Allow time for serial port to settle

# Function to map values
def map_value(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Main loop
try:
    while True:
        # Read joystick 1 X axis
        joy_val = joy1_x.value  # 0 to ~26400
        
        # Constrain
        joy_val = max(0, min(joy_val, 26400))

        # Map to 0-180 for servo
        angle = map_value(joy_val, 0, 26400, 0, 180)

        # Send angle to Artemis
        ser.write(f"{joy_val}\n".encode())

        print(f"Joystick value: {joy_val} -> Sending to servo angle...")

        time.sleep(0.02)  # 20 ms = 50 updates per second

except KeyboardInterrupt:
    print("Stopped by user.")
    ser.close()
                                                         