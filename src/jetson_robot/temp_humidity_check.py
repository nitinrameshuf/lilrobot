#!/usr/bin/env python3
"""
AHT20 Temperature and Humidity Sensor Reader
Direct connection to Jetson Orin Nano Super

Wiring:
- AHT20 VCC → Jetson Pin 1 (3.3V)
- AHT20 GND → Jetson Pin 6 (GND)  
- AHT20 SDA → Jetson Pin 3 (I2C Bus 7)
- AHT20 SCL → Jetson Pin 5 (I2C Bus 7)
"""

import smbus
import time
import sys

class AHT20:
    def __init__(self, bus_number=7, address=0x38):
        """Initialize AHT20 sensor"""
        self.bus = smbus.SMBus(bus_number)
        self.address = address
        self.initialize()
    
    def initialize(self):
        """Initialize the AHT20 sensor"""
        try:
            # Send initialization command
            self.bus.write_i2c_block_data(self.address, 0xBE, [0x08, 0x00])
            time.sleep(0.01)
            print("AHT20 sensor initialized successfully")
        except Exception as e:
            print(f"Error initializing AHT20: {e}")
            sys.exit(1)
    
    def read_data(self):
        """Read temperature and humidity from AHT20"""
        try:
            # Trigger measurement
            self.bus.write_i2c_block_data(self.address, 0xAC, [0x33, 0x00])
            time.sleep(0.1)  # Wait for measurement to complete
            
            # Read 6 bytes of data
            data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
            
            # Check if measurement is valid
            if data[0] & 0x80:
                print("Sensor busy, retrying...")
                time.sleep(0.05)
                return self.read_data()
            
            # Extract humidity data (bits 19:0)
            humidity_raw = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4))
            
            # Extract temperature data (bits 19:0)
            temp_raw = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5])
            
            # Convert to actual values
            humidity = (humidity_raw * 100.0) / 1048576.0  # Convert to %RH
            temperature = ((temp_raw * 200.0) / 1048576.0) - 50.0  # Convert to °C
            
            return temperature, humidity
            
        except Exception as e:
            print(f"Error reading AHT20 data: {e}")
            return None, None
    
    def read_celsius(self):
        """Get temperature in Celsius"""
        temp, _ = self.read_data()
        return temp
    
    def read_fahrenheit(self):
        """Get temperature in Fahrenheit"""
        temp_c, _ = self.read_data()
        if temp_c is not None:
            return (temp_c * 9/5) + 32
        return None
    
    def read_humidity(self):
        """Get humidity percentage"""
        _, humidity = self.read_data()
        return humidity

def main():
    """Main program loop"""
    print("AHT20 Temperature and Humidity Sensor Reader")
    print("=" * 50)
    print("Wiring Check:")
    print("- AHT20 VCC → Jetson Pin 1 (3.3V)")
    print("- AHT20 GND → Jetson Pin 6 (GND)")
    print("- AHT20 SDA → Jetson Pin 3 (I2C Bus 7)")
    print("- AHT20 SCL → Jetson Pin 5 (I2C Bus 7)")
    print("=" * 50)
    
    try:
        # Initialize sensor on I2C Bus 7 (pins 3,5)
        sensor = AHT20(bus_number=7, address=0x38)
        
        print("\nReading sensor data... (Press Ctrl+C to stop)\n")
        
        while True:
            # Read sensor data
            temp_c, humidity = sensor.read_data()
            
            if temp_c is not None and humidity is not None:
                temp_f = (temp_c * 9/5) + 32
                
                # Display readings
                print(f"Temperature: {temp_c:.2f}°C ({temp_f:.2f}°F)")
                print(f"Humidity:    {humidity:.2f}%RH")
                print(f"Time:        {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 40)
            else:
                print("Failed to read sensor data")
            
            # Wait 2 seconds before next reading
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Program ended")

if __name__ == "__main__":
    main()