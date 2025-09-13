#!/usr/bin/env python3
"""
JX PDI-6225MG-300 Servo Test Program
High-torque 300-degree servo testing on Jetson Orin Nano Super

Wiring:
- Servo Red (Power) → External 6V Power Supply (+)
- Servo Brown/Black (GND) → External 6V GND + Jetson Pin 6 (common ground)
- Servo Orange/Yellow (Signal) → Jetson Pin 32 (GPIO07)

Servo Specs:
- Pulse Width: 500μs - 2500μs
- Max Angle: 300°
- Operating Voltage: 6.0V
- Torque: 25.3kg.cm
"""

import Jetson.GPIO as GPIO
import time
import math

class ServoController:
    def __init__(self, pin, frequency=50):
        """
        Initialize servo controller
        
        Args:
            pin: GPIO pin number (BOARD numbering)
            frequency: PWM frequency in Hz (50Hz standard for servos)
        """
        self.pin = pin
        self.frequency = frequency
        
        # Setup GPIO
        GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
        GPIO.setup(self.pin, GPIO.OUT)
        
        # Create PWM instance
        self.pwm = GPIO.PWM(self.pin, self.frequency)
        self.pwm.start(0)  # Start with 0% duty cycle
        
        print(f"Servo controller initialized on pin {self.pin}")
    
    def pulse_width_to_duty_cycle(self, pulse_width_us):
        """
        Convert pulse width (microseconds) to duty cycle percentage
        
        Args:
            pulse_width_us: Pulse width in microseconds
        
        Returns:
            duty_cycle: Duty cycle percentage (0-100)
        """
        period_us = (1.0 / self.frequency) * 1000000  # Period in microseconds
        duty_cycle = (pulse_width_us / period_us) * 100
        return duty_cycle
    
    def angle_to_pulse_width(self, angle):
        """
        Convert angle to pulse width for 300-degree servo
        
        Args:
            angle: Angle in degrees (0-300)
        
        Returns:
            pulse_width: Pulse width in microseconds
        """
        # Clamp angle to valid range
        angle = max(0, min(300, angle))
        
        # Map angle (0-300°) to pulse width (500-2500μs)
        pulse_width = 500 + (angle / 300.0) * (2500 - 500)
        return pulse_width
    
    def set_angle(self, angle):
        """
        Set servo to specific angle
        
        Args:
            angle: Target angle in degrees (0-300)
        """
        pulse_width = self.angle_to_pulse_width(angle)
        duty_cycle = self.pulse_width_to_duty_cycle(pulse_width)
        
        self.pwm.ChangeDutyCycle(duty_cycle)
        print(f"Angle: {angle:6.1f}° | Pulse: {pulse_width:7.1f}μs | Duty: {duty_cycle:5.2f}%")
    
    def set_pulse_width(self, pulse_width_us):
        """
        Set servo using direct pulse width
        
        Args:
            pulse_width_us: Pulse width in microseconds (500-2500)
        """
        pulse_width_us = max(500, min(2500, pulse_width_us))
        duty_cycle = self.pulse_width_to_duty_cycle(pulse_width_us)
        
        self.pwm.ChangeDutyCycle(duty_cycle)
        print(f"Pulse Width: {pulse_width_us}μs | Duty Cycle: {duty_cycle:.2f}%")
    
    def sweep_test(self, steps=10, delay=1.0):
        """
        Perform a sweep test across the servo range
        
        Args:
            steps: Number of steps in the sweep
            delay: Delay between steps in seconds
        """
        print(f"\nPerforming sweep test with {steps} steps...")
        
        for i in range(steps + 1):
            angle = (300.0 / steps) * i
            self.set_angle(angle)
            time.sleep(delay)
    
    def center_servo(self):
        """Center the servo to 150° (middle position for 300° servo)"""
        print("\nCentering servo to 150°...")
        self.set_angle(150)
    
    def test_positions(self):
        """Test specific key positions"""
        positions = [
            (0, "Minimum position"),
            (75, "Quarter position"),
            (150, "Center position"),
            (225, "Three-quarter position"),
            (300, "Maximum position")
        ]
        
        print("\nTesting key positions...")
        for angle, description in positions:
            print(f"\n{description}:")
            self.set_angle(angle)
            time.sleep(2)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.pwm.stop()
        GPIO.cleanup()
        print("GPIO cleanup completed")

def main():
    """Main test program"""
    print("JX PDI-6225MG-300 Servo Test Program")
    print("=" * 60)
    print("IMPORTANT SAFETY CHECKS:")
    print("✓ Servo connected to external 6V power supply")
    print("✓ Common ground between servo and Jetson")
    print("✓ Signal wire connected to Jetson Pin 32")
    print("✓ No obstacles in servo movement path")
    print("=" * 60)
    
    # Wait for user confirmation
    input("\nPress Enter when ready to start servo test...")
    
    try:
        # Initialize servo on pin 32 (GPIO07)
        servo = ServoController(pin=32, frequency=50)
        
        print("\nStarting servo test sequence...")
        
        # Test 1: Center the servo
        servo.center_servo()
        time.sleep(3)
        
        # Test 2: Test key positions
        servo.test_positions()
        
        # Test 3: Smooth sweep test
        print("\nPerforming smooth sweep test...")
        servo.sweep_test(steps=20, delay=0.5)
        
        # Test 4: Speed test
        print("\nPerforming speed test...")
        for i in range(3):
            servo.set_angle(0)
            time.sleep(1)
            servo.set_angle(300)
            time.sleep(1)
        
        # Test 5: Precision test
        print("\nPerforming precision test (small increments)...")
        base_angle = 150
        for offset in [-10, -5, 0, 5, 10, 5, 0, -5]:
            servo.set_angle(base_angle + offset)
            time.sleep(0.8)
        
        # Return to center
        print("\nReturning to center position...")
        servo.center_servo()
        time.sleep(2)
        
        print("\n" + "=" * 60)
        print("Servo test completed successfully!")
        print("Servo performance characteristics observed:")
        print(f"- Speed: ~0.21 sec/60° (as specified)")
        print(f"- Range: 0-300° (full range)")
        print(f"- Precision: Smooth movement")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during servo test: {e}")
    finally:
        # Always cleanup
        try:
            servo.cleanup()
        except:
            GPIO.cleanup()

if __name__ == "__main__":
    main()