#!/usr/bin/env python3
"""
JX PDI-6225MG-300 Servo Test on Pin 7
Using GPIO line 144 (PAC.06) which is confirmed working
"""

import subprocess
import time
import sys

def run_gpio_command(command):
    """Run gpio command and handle errors"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

def generate_servo_pwm(pulse_width_ms, duration_seconds=3):
    """Generate PWM signal for servo using gpioset on Pin 7 (GPIO 144)"""
    print(f"Generating {pulse_width_ms}ms pulses on Pin 7 (GPIO 144)")
    
    cycles = int(duration_seconds * 50)  # 50Hz = 50 cycles per second
    period_ms = 20  # 50Hz = 20ms period
    gpio_line = 144  # Pin 7 = GPIO line 144
    
    for i in range(cycles):
        # HIGH for pulse width
        run_gpio_command(f"gpioset gpiochip0 {gpio_line}=1")
        time.sleep(pulse_width_ms / 1000.0)
        
        # LOW for remainder of period
        run_gpio_command(f"gpioset gpiochip0 {gpio_line}=0")
        time.sleep((period_ms - pulse_width_ms) / 1000.0)
        
        # Progress indicator every 25 cycles
        if i % 25 == 0:
            print(f"  Progress: {i+1}/{cycles}", end='\r')
    
    print(f"  Completed: {cycles}/{cycles}")

def test_basic_output():
    """Test basic HIGH/LOW output on Pin 7"""
    print("Testing basic output on Pin 7 (GPIO 144)")
    gpio_line = 144
    
    for i in range(3):
        print(f"Setting HIGH {i+1}/3...")
        success, _ = run_gpio_command(f"gpioset gpiochip0 {gpio_line}=1")
        if not success:
            print("Failed to set HIGH")
            return False
        time.sleep(1)
        
        print(f"Setting LOW {i+1}/3...")
        success, _ = run_gpio_command(f"gpioset gpiochip0 {gpio_line}=0")
        if not success:
            print("Failed to set LOW")
            return False
        time.sleep(1)
    
    return True

def test_servo_positions():
    """Test servo at different positions"""
    print("\nTesting servo positions...")
    print("Watch your servo for movement!")
    
    # Test positions: pulse_width_ms, description, angle
    positions = [
        (1.5, "Center position (150°)", "servo should move to middle"),
        (0.5, "Minimum position (0°)", "servo should move to one extreme"),
        (2.5, "Maximum position (300°)", "servo should move to other extreme"),
        (1.0, "Quarter position (75°)", "servo should move to quarter position"),
        (2.0, "Three-quarter position (225°)", "servo should move to three-quarter position"),
        (1.5, "Back to center (150°)", "servo should return to middle")
    ]
    
    for pulse_ms, description, expected in positions:
        print(f"\n{description}")
        print(f"Expected: {expected}")
        print(f"Pulse width: {pulse_ms}ms")
        
        generate_servo_pwm(pulse_ms, duration_seconds=3)
        
        response = input("Did servo move as expected? (y/n/q to quit): ").lower()
        if response == 'q':
            break
        elif response == 'y':
            print("✓ Position test successful!")
        else:
            print("✗ Position test failed")
        
        time.sleep(0.5)  # Brief pause between positions

def main():
    print("JX PDI-6225MG-300 Servo Test on Pin 7")
    print("=" * 50)
    print("Servo Connection:")
    print("- Red wire: External 5V power supply")
    print("- Brown/Black wire: Common ground (external GND + Jetson Pin 6)")
    print("- Yellow/Orange wire: Jetson Pin 7")
    print()
    print("Pin 7 = GPIO line 144 (PAC.06)")
    print("=" * 50)
    
    # Check if gpioset is available
    success, _ = run_gpio_command("which gpioset")
    if not success:
        print("ERROR: gpioset not found. Install with:")
        print("sudo apt install gpiod")
        sys.exit(1)
    
    input("Press Enter when servo is connected to Pin 7...")
    
    try:
        # Test 1: Basic GPIO functionality
        print("Step 1: Testing basic GPIO output")
        if not test_basic_output():
            print("Basic GPIO test failed!")
            return
        print("✓ Basic GPIO test passed")
        
        input("\nPress Enter to start servo PWM test...")
        
        # Test 2: Servo PWM test
        print("Step 2: Testing servo positions")
        test_servo_positions()
        
        print("\n" + "=" * 50)
        print("Servo test completed!")
        print()
        print("If servo worked:")
        print("✓ Pin 7 (GPIO 144) is functional for servo control")
        print("✓ You can use this pin for your robot project")
        print()
        print("If servo didn't work:")
        print("- Check 5V power supply capacity (needs 2A+)")
        print("- Verify common ground connection")
        print("- Test servo with known working controller")
        print("- Check servo power consumption vs supply capability")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        # Ensure GPIO is set LOW on exit
        run_gpio_command("gpioset gpiochip0 144=0")
    except Exception as e:
        print(f"Test failed with error: {e}")
        # Ensure GPIO is set LOW on exit
        run_gpio_command("gpioset gpiochip0 144=0")

if __name__ == "__main__":
    main()