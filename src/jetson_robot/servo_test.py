#!/usr/bin/env python3
"""
GPIO LED Test for Pin 32 debugging
Tests multiple methods to get GPIO working on Jetson Orin Nano Super
"""

import subprocess
import time
import sys
import os

def run_command(cmd, description=""):
    """Run a command and return success status and output"""
    try:
        print(f"\n{'='*50}")
        print(f"TESTING: {description}")
        print(f"Command: {cmd}")
        print(f"{'='*50}")
        
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("SUCCESS:")
        print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print("FAILED:")
        print(f"Return code: {e.returncode}")
        print(f"STDERR: {e.stderr}")
        print(f"STDOUT: {e.stdout}")
        return False, e.stderr

def test_gpio_lines():
    """Test different GPIO lines to find which ones work"""
    print("\n" + "="*60)
    print("TESTING DIFFERENT GPIO LINES")
    print("="*60)
    
    # Test lines that showed as "unused output" in gpioinfo
    test_lines = [
        (41, "PG.06", "Pin 32 expected mapping"),
        (49, "PH.06", "Alternative unused output"),  
        (68, "PK.04", "Another unused output"),
        (69, "PK.05", "Another unused output"),
        (103, "PQ.03", "Another unused output"),
        (138, "PAC.00", "Another unused output")
    ]
    
    working_lines = []
    
    for line, name, description in test_lines:
        print(f"\n--- Testing GPIO line {line} ({name}) - {description} ---")
        
        # Try to set HIGH
        success, output = run_command(f"gpioset gpiochip0 {line}=1", f"Set line {line} HIGH")
        if success:
            print(f"✓ Successfully set line {line} HIGH")
            print("Check LED - should be ON")
            input("Press Enter after checking LED...")
            
            # Try to set LOW
            success_low, output_low = run_command(f"gpioset gpiochip0 {line}=0", f"Set line {line} LOW")
            if success_low:
                print(f"✓ Successfully set line {line} LOW")
                print("Check LED - should be OFF")
                working_lines.append((line, name, description))
                input("Press Enter after checking LED...")
            else:
                print(f"✗ Failed to set line {line} LOW")
        else:
            print(f"✗ Failed to set line {line} HIGH")
    
    return working_lines

def test_jetson_gpio_library():
    """Test using Jetson.GPIO library"""
    print("\n" + "="*60)
    print("TESTING JETSON.GPIO LIBRARY")
    print("="*60)
    
    try:
        # Set environment variable
        os.environ['JETSON_MODEL_NAME'] = 'JETSON_ORIN_NANO'
        
        import Jetson.GPIO as GPIO
        print("✓ Jetson.GPIO imported successfully")
        
        # Test Pin 32
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(32, GPIO.OUT)
        print("✓ Pin 32 configured as output")
        
        print("Setting Pin 32 HIGH...")
        GPIO.output(32, GPIO.HIGH)
        print("Check LED with multimeter - should read 3.3V")
        input("Press Enter after checking...")
        
        print("Setting Pin 32 LOW...")
        GPIO.output(32, GPIO.LOW)
        print("Check LED with multimeter - should read 0V")
        input("Press Enter after checking...")
        
        # Test other pins
        test_pins = [33, 15, 16, 18, 22]  # Other GPIO-capable pins
        working_pins = []
        
        for pin in test_pins:
            try:
                print(f"\n--- Testing Pin {pin} ---")
                GPIO.setup(pin, GPIO.OUT)
                
                GPIO.output(pin, GPIO.HIGH)
                print(f"Pin {pin} set HIGH - check LED")
                response = input("Did LED turn ON? (y/n): ").lower()
                
                GPIO.output(pin, GPIO.LOW)
                print(f"Pin {pin} set LOW - check LED")
                
                if response == 'y':
                    working_pins.append(pin)
                    print(f"✓ Pin {pin} works!")
                else:
                    print(f"✗ Pin {pin} doesn't work")
                    
            except Exception as e:
                print(f"✗ Pin {pin} failed: {e}")
        
        GPIO.cleanup()
        return True, working_pins
        
    except Exception as e:
        print(f"✗ Jetson.GPIO test failed: {e}")
        return False, []

def test_hardware_pwm():
    """Check for hardware PWM devices"""
    print("\n" + "="*60)
    print("CHECKING HARDWARE PWM")
    print("="*60)
    
    pwm_paths = [
        "/sys/class/pwm/",
        "/sys/devices/3280000.pwm/",
        "/sys/devices/32c0000.pwm/"
    ]
    
    found_pwm = False
    for path in pwm_paths:
        if os.path.exists(path):
            print(f"✓ Found PWM device: {path}")
            try:
                contents = os.listdir(path)
                print(f"  Contents: {contents}")
                found_pwm = True
            except:
                print(f"  Could not list contents")
        else:
            print(f"✗ PWM path not found: {path}")
    
    return found_pwm

def check_pin_configuration():
    """Check current pin configuration and multiplexing"""
    print("\n" + "="*60)
    print("CHECKING PIN CONFIGURATION")
    print("="*60)
    
    # Check pinmux configuration
    pinmux_files = [
        "/sys/kernel/debug/pinctrl/2430000.pinctrl/pinmux-pins",
        "/sys/kernel/debug/pinctrl/2430000.pinctrl/pins"
    ]
    
    for file_path in pinmux_files:
        if os.path.exists(file_path):
            success, output = run_command(f"sudo cat {file_path} | grep -i 'pg.06\\|ph.00\\|pac.06'", 
                                        f"Check pinmux for relevant pins in {file_path}")
            if not success:
                print("No specific pin info found or grep failed")
        else:
            print(f"Pinmux file not found: {file_path}")

def main():
    print("GPIO LED TEST - JETSON ORIN NANO SUPER")
    print("="*60)
    print("LED Setup:")
    print("- LED + resistor connected to Pin 32")
    print("- Other end to GND (Pin 6)")
    print("- Multimeter ready to test voltage")
    print("="*60)
    
    # Check if running with sufficient permissions
    if os.geteuid() != 0:
        print("Note: Some tests may require sudo privileges")
    
    input("\nPress Enter to start GPIO testing...")
    
    results = {
        "libgpiod_lines": [],
        "jetson_gpio_pins": [],
        "pwm_available": False
    }
    
    try:
        # Test 1: Check pin configuration
        check_pin_configuration()
        
        # Test 2: Hardware PWM check
        results["pwm_available"] = test_hardware_pwm()
        
        # Test 3: Test different GPIO lines with libgpiod
        print("\n\nMove LED to Pin 32 and test different GPIO lines...")
        input("Press Enter when LED is connected to Pin 32...")
        results["libgpiod_lines"] = test_gpio_lines()
        
        # Test 4: Test Jetson.GPIO library
        jetson_success, working_pins = test_jetson_gpio_library()
        results["jetson_gpio_pins"] = working_pins
        
        # Summary
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        print(f"Hardware PWM available: {results['pwm_available']}")
        
        if results["libgpiod_lines"]:
            print("Working GPIO lines (libgpiod):")
            for line, name, desc in results["libgpiod_lines"]:
                print(f"  - Line {line} ({name}): {desc}")
        else:
            print("No working GPIO lines found with libgpiod")
        
        if results["jetson_gpio_pins"]:
            print("Working pins (Jetson.GPIO):")
            for pin in results["jetson_gpio_pins"]:
                print(f"  - Pin {pin}")
        else:
            print("No working pins found with Jetson.GPIO")
        
        if results["libgpiod_lines"] or results["jetson_gpio_pins"]:
            print("\n✓ SUCCESS: Found working GPIO!")
            if results["jetson_gpio_pins"]:
                print(f"Recommendation: Use Pin {results['jetson_gpio_pins'][0]} with Jetson.GPIO library")
            elif results["libgpiod_lines"]:
                line, name, desc = results["libgpiod_lines"][0]
                print(f"Recommendation: Use GPIO line {line} with libgpiod")
        else:
            print("\n✗ NO WORKING GPIO FOUND")
            print("Possible issues:")
            print("- Pin permissions/configuration problem")
            print("- Hardware issue with board")
            print("- GPIO already in use by system")
            print("- Need different pinmux configuration")
        
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    main()