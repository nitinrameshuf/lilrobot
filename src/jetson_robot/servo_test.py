#!/usr/bin/env python3
"""
JX PDI-6225MG-300 Servo Test using libgpiod
Uses the correct GPIO line numbers from gpioinfo
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

def generate_servo_pwm(gpio_line, pulse_width_ms, duration_seconds=3):
    """Generate PWM signal for servo using gpioset"""
    print(f"Generating {pulse_width_ms}ms pulses on GPIO line {gpio_line}")
    
    cycles = int(duration_seconds * 50)  # 50Hz = 50 cycles per second
    period_ms = 20  # 50Hz = 20ms period
    
    for i in range(cycles):
        # HIGH for pulse width
        run_gpio_command(f"gpioset gpiochip0 {gpio_line}=1")
        time.sleep(pulse_width_ms / 1000.0)
        
        # LOW for remainder of period
        run_gpio_command(f"gpioset gpiochip0 {gpio_line}=0")
        time.sleep((period_ms - pulse_width_ms) / 1000.0)
        
        # Progress indicator
        if i % 10 == 0:
            print(f"  Progress: {i+1}/{cycles}", end='\r')
    
    print(f"  Completed: {cycles}/{cycles}")

def test_servo_positions(pin_number, gpio_line):
    """Test servo at different positions"""
    print(f"\nTesting servo on Pin {pin_number} (GPIO line {gpio_line})")
    print("=" * 50)
    
    # Test positions: pulse_width_ms, description, angle
    positions = [
        (0.5, "Minimum position (0°)"),
        (1.0, "Quarter position (75°)"),
        (1.5, "Center position (150°)"),
        (2.0, "Three-quarter position (225°)"),
        (2.5, "Maximum position (300°)")
    ]
    
    for pulse_ms, description in positions:
        print(f"\n{description} - {pulse_ms}ms pulse")
        generate_servo_pwm(gpio_line, pulse_ms, duration_seconds=3)
        time.sleep(0.5)  # Brief pause between positions

def test_pin_basic_output(pin_number, gpio_line):
    """Test basic HIGH/LOW output"""
    print(f"\nTesting basic output on Pin {pin_number} (GPIO line {gpio_line})")
    print("Check with multimeter - should see 3.3V HIGH, 0V LOW")
    
    for i in range(5):
        success, output = run_gpio_command(f"gpioset gpiochip0 {gpio_line}=1")
        if success:
            print(f"HIGH {i+1} - should read 3.3V")
        else:
            print(f"ERROR setting HIGH: {output}")
            return False
        time.sleep(1)
        
        success, output = run_gpio_command(f"gpioset gpiochip0 {gpio_line}=0")
        if success:
            print(f"LOW {i+1} - should read 0V")
        else:
            print(f"ERROR setting LOW: {output}")
            return False
        time.sleep(1)
    
    return True

def main():
    print("JX PDI-6225MG-300 Servo Test using libgpiod")
    print("=" * 60)
    
    # GPIO mappings from gpioinfo
    pin_options = {
        "32": {"gpio_line": 41, "name": "PG.06"},
        "33": {"gpio_line": 43, "name": "PH.00"}
    }
    
    print("Available pins:")
    for pin, info in pin_options.items():
        print(f"  Pin {pin}: GPIO line {info['gpio_line']} ({info['name']})")
    
    # Check if gpioset is available
    success, _ = run_gpio_command("which gpioset")
    if not success:
        print("\nERROR: gpioset not found. Install with:")
        print("sudo apt install gpiod")
        sys.exit(1)
    
    pin_choice = input(f"\nWhich pin is your servo connected to? (32/33): ").strip()
    
    if pin_choice not in pin_options:
        print("Invalid pin choice. Using Pin 33 (recommended)")
        pin_choice = "33"
    
    gpio_line = pin_options[pin_choice]["gpio_line"]
    gpio_name = pin_options[pin_choice]["name"]
    
    print(f"\nUsing Pin {pin_choice}: GPIO line {gpio_line} ({gpio_name})")
    print("\nEnsure your servo wiring:")
    print(f"  - Red wire: External 5V power")
    print(f"  - Brown/Black wire: Common ground (external GND + Jetson Pin 6)")
    print(f"  - Yellow/Orange wire: Jetson Pin {pin_choice}")
    
    input("\nPress Enter to start test...")
    
    try:
        # Test 1: Basic GPIO functionality
        if not test_pin_basic_output(pin_choice, gpio_line):
            print("Basic GPIO test failed. Check connections.")
            return
        
        input("\nPress Enter to start servo PWM test...")
        
        # Test 2: Servo PWM test
        test_servo_positions(pin_choice, gpio_line)
        
        print(f"\n" + "=" * 60)
        print("Servo test completed!")
        print("If servo didn't move:")
        print("1. Check 5V power supply (needs 2A+ capacity)")
        print("2. Verify common ground connection")
        print("3. Try the other pin (32 or 33)")
        print("4. Test servo with known working controller")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    main()