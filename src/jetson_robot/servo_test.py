#!/usr/bin/env python3
"""
Servo PWM Signal Test - Focused on PWM generation
JX PDI-6225MG-300 operates on 4.8V-6.0V (your 5V is fine)

The issue is likely PWM signal generation, not power.
"""

import os
import time

# Set environment
os.environ['JETSON_MODEL_NAME'] = 'JETSON_ORIN_NANO'

def manual_servo_pwm():
    """Generate servo PWM manually using sysfs"""
    print("Manual Servo PWM Test")
    print("=" * 40)
    
    gpio_num = 389  # Pin 32 on Jetson Orin Nano
    
    try:
        # Setup GPIO
        os.system(f"echo {gpio_num} | sudo tee /sys/class/gpio/export")
        time.sleep(0.1)
        os.system(f"echo out | sudo tee /sys/class/gpio/gpio{gpio_num}/direction")
        
        print("Generating servo control signals...")
        print("Watch your servo for movement!")
        
        # Test sequence with different pulse widths
        test_positions = [
            (0.5, "Minimum (0°) - 0.5ms pulse"),
            (1.0, "Low (60°) - 1.0ms pulse"), 
            (1.5, "Center (150°) - 1.5ms pulse"),
            (2.0, "High (240°) - 2.0ms pulse"),
            (2.5, "Maximum (300°) - 2.5ms pulse")
        ]
        
        for pulse_ms, description in test_positions:
            print(f"\n{description}")
            
            # Send PWM for 3 seconds
            cycles = 150  # 3 seconds at 50Hz
            for i in range(cycles):
                # HIGH pulse
                os.system(f"echo 1 | sudo tee /sys/class/gpio/gpio{gpio_num}/value")
                time.sleep(pulse_ms / 1000.0)  # Pulse width
                
                # LOW for rest of 20ms period
                os.system(f"echo 0 | sudo tee /sys/class/gpio/gpio{gpio_num}/value")
                time.sleep((20 - pulse_ms) / 1000.0)  # 50Hz = 20ms period
                
                if i % 25 == 0:  # Progress indicator
                    print(f"  Cycle {i+1}/{cycles}", end='\r')
            
            print(f"  ✓ Completed {description}")
            time.sleep(1)
        
        # Cleanup
        os.system(f"echo {gpio_num} | sudo tee /sys/class/gpio/unexport")
        print("\n✓ Test completed")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def test_with_jetson_gpio():
    """Test using Jetson.GPIO if available"""
    print("\nJetson.GPIO PWM Test")
    print("=" * 40)
    
    try:
        import Jetson.GPIO as GPIO
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(32, GPIO.OUT)
        
        # Create PWM object - 50Hz for servo
        pwm = GPIO.PWM(32, 50)
        pwm.start(0)
        
        print("Testing with Jetson.GPIO PWM...")
        
        # Test different duty cycles for servo positions
        # Servo expects 1-2ms pulses in 20ms period (5-10% duty cycle)
        positions = [
            (2.5, "Minimum position (0.5ms pulse)"),
            (5.0, "Low position (1.0ms pulse)"),
            (7.5, "Center position (1.5ms pulse)"),
            (10.0, "High position (2.0ms pulse)"), 
            (12.5, "Maximum position (2.5ms pulse)")
        ]
        
        for duty, description in positions:
            print(f"{description} - Duty cycle: {duty}%")
            pwm.ChangeDutyCycle(duty)
            time.sleep(3)
        
        # Stop PWM and cleanup
        pwm.stop()
        GPIO.cleanup()
        print("✓ Jetson.GPIO test completed")
        
    except Exception as e:
        print(f"✗ Jetson.GPIO failed: {e}")
        return False
    
    return True

def quick_signal_test():
    """Quick test to verify signal output"""
    print("\nQuick Signal Test")
    print("=" * 40)
    print("Use multimeter on Pin 32 to verify signal")
    
    gpio_num = 389
    
    try:
        os.system(f"echo {gpio_num} | sudo tee /sys/class/gpio/export")
        time.sleep(0.1)
        os.system(f"echo out | sudo tee /sys/class/gpio/gpio{gpio_num}/direction")
        
        print("Toggling Pin 32 - check with multimeter:")
        for i in range(10):
            print(f"HIGH (should read 3.3V)")
            os.system(f"echo 1 | sudo tee /sys/class/gpio/gpio{gpio_num}/value")
            time.sleep(1)
            
            print(f"LOW (should read 0V)")  
            os.system(f"echo 0 | sudo tee /sys/class/gpio/gpio{gpio_num}/value")
            time.sleep(1)
        
        os.system(f"echo {gpio_num} | sudo tee /sys/class/gpio/unexport")
        
    except Exception as e:
        print(f"✗ Signal test failed: {e}")

def main():
    print("JX PDI-6225MG-300 Servo PWM Test")
    print("=" * 50)
    print("Servo specs: 4.8V-6.0V (your 5V is fine)")
    print("Pulse width: 500μs-2500μs") 
    print("Max angle: 300°")
    print("=" * 50)
    
    print("\nWiring check:")
    print("- Red wire → 5V external power ✓")
    print("- Brown/Black wire → GND (power + Jetson Pin 6) ✓") 
    print("- Yellow wire → Jetson Pin 32 ✓")
    
    choice = input("\nSelect test:\n1. Manual PWM (recommended)\n2. Jetson.GPIO PWM\n3. Quick signal test\n4. All tests\nChoice (1-4): ")
    
    if choice == "1":
        manual_servo_pwm()
    elif choice == "2":
        test_with_jetson_gpio()
    elif choice == "3":
        quick_signal_test()
    elif choice == "4":
        quick_signal_test()
        input("\nPress Enter to continue to manual PWM test...")
        manual_servo_pwm()
        input("\nPress Enter to continue to Jetson.GPIO test...")
        test_with_jetson_gpio()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()