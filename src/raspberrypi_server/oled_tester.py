import board
import busio
import time
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

# ======== Initialize 128x32 Display ========
def initialize_128x32_display():
    """
    Initialize the 128x32 OLED display
    """
    i2c = busio.I2C(board.SCL, board.SDA)
    
    # Try common I2C addresses
    addresses_to_try = [0x3C, 0x3D]
    
    for addr in addresses_to_try:
        try:
            print(f"Trying 128x32 display at address 0x{addr:02X}...")
            
            oled = SSD1306_I2C(128, 32, i2c, addr=addr)
            
            # Test basic functionality
            oled.fill(0)
            oled.show()
            time.sleep(0.2)
            
            oled.fill(1)
            oled.show()
            time.sleep(0.2)
            
            oled.fill(0)
            oled.show()
            
            print(f"SUCCESS! 128x32 display working at address 0x{addr:02X}")
            return oled
            
        except Exception as e:
            print(f"Failed at address 0x{addr:02X}: {e}")
            continue
    
    print("Could not initialize 128x32 display")
    return None

# ======== Display Test Function ========
def test_128x32_display(oled):
    """
    Test the 128x32 display with various patterns
    """
    font = ImageFont.load_default()
    
    print("Testing 128x32 display functionality...")
    
    # Test 1: Clear display
    print("Test 1: Clear display")
    oled.fill(0)
    oled.show()
    time.sleep(1)
    
    # Test 2: Full display
    print("Test 2: Full white display")
    oled.fill(1)
    oled.show()
    time.sleep(1)
    
    # Test 3: Border test
    print("Test 3: Border test")
    image = Image.new("1", (128, 32))
    draw = ImageDraw.Draw(image)
    draw.rectangle([(0, 0), (127, 31)], outline=1, fill=0)
    oled.image(image)
    oled.show()
    time.sleep(2)
    
    # Test 4: Multi-line text test (128x32 can fit about 4 lines)
    print("Test 4: Multi-line text test")
    image = Image.new("1", (128, 32))
    draw = ImageDraw.Draw(image)
    
    # 3 lines of text for 128x32 display (optimal fit)
    draw.text((0, 0), "Line 1", font=font, fill=1)
    draw.text((0, 10), "Line 2", font=font, fill=1)
    draw.text((0, 20), "Line 3", font=font, fill=1)
    
    oled.image(image)
    oled.show()
    time.sleep(3)
    
    # Test 5: Your original text
    print("Test 5: Original text test")
    messages = ["Hi how are you", "how are you", "how do you do"]
    
    # Display each message separately (since 128x32 has limited space)
    for msg in messages:
        oled.fill(0)
        oled.show()
        time.sleep(0.5)
        
        image = Image.new("1", (128, 32))
        draw = ImageDraw.Draw(image)
        draw.text((0, 8), msg, font=font, fill=1)  # Center vertically
        oled.image(image)
        oled.show()
        time.sleep(2)
    
    # Test 6: All three lines at once
    print("Test 6: All three lines at once")
    image = Image.new("1", (128, 32))
    draw = ImageDraw.Draw(image)
    
    draw.text((0, 0), "Hi how are you", font=font, fill=1)
    draw.text((0, 10), "how are you", font=font, fill=1)
    draw.text((0, 20), "how do you do", font=font, fill=1)
    
    oled.image(image)
    oled.show()
    time.sleep(5)
    
    # Clear at end
    oled.fill(0)
    oled.show()

# ======== Optimized Drawing Function for 128x32 ========
def draw_text_128x32(oled, text, font):
    """
    Draw text optimized for 128x32 display
    Can fit approximately 4 lines of 8-pixel high text
    """
    image = Image.new("1", (128, 32))
    draw = ImageDraw.Draw(image)
    
    lines = text.split('\n')
    y = 0  # Start from very top to give capital letters full space
    line_height = 10  # Better spacing for 128x32 display
    max_lines = 3  # Exactly 3 lines fit perfectly in 128x32
    
    for i, line in enumerate(lines):
        if i >= max_lines or y + line_height > 32:
            break
        draw.text((0, y), line, font=font, fill=1)
        y += line_height
    
    oled.image(image)
    oled.show()

# ======== Scrolling Text Function ========
def scroll_text_128x32(oled, text, font, delay=2):
    """
    Scroll through multiple lines of text on 128x32 display
    """
    lines = text.split('\n')
    
    for line in lines:
        oled.fill(0)
        oled.show()
        time.sleep(0.3)
        
        image = Image.new("1", (128, 32))
        draw = ImageDraw.Draw(image)
        # Center text vertically on the 32-pixel height
        draw.text((0, 12), line, font=font, fill=1)
        
        oled.image(image)
        oled.show()
        time.sleep(delay)
    
    # Clear at the end
    oled.fill(0)
    oled.show()

# ======== Main Test Function ========
def main():
    print("Testing new 0.91\" 128x32 OLED display...")
    
    # Initialize the 128x32 display
    oled = initialize_128x32_display()
    
    if oled is None:
        print("Could not initialize display. Check wiring:")
        print("- VCC to 3.3V or 5V")
        print("- GND to Ground") 
        print("- SCL to GPIO 3 (SCL)")
        print("- SDA to GPIO 2 (SDA)")
        return
    
    print("\n128x32 Display initialized successfully!")
    print("Running comprehensive tests...")
    
    # Run comprehensive tests
    # test_128x32_display(oled) # Uncomment to run full test suite
    
    print("\n" + "="*50)
    print("TESTING YOUR ORIGINAL TEXT")
    print("="*50)
    
    font = ImageFont.load_default()
    test_text = "Hi how are you\nhow are you\nhow do you do"
    
    # Test 1: All lines at once
    print("Test 1: All three lines at once...")
    draw_text_128x32(oled, test_text, font)
    time.sleep(5)
    
    # Test 2: Scrolling through each line
    print("Test 2: Scrolling through each line...")
    scroll_text_128x32(oled, test_text, font, delay=3)
    
    print("\n" + "="*50)
    print("FRAGMENTATION TEST")
    print("="*50)
    print("Check the display now!")
    print("Is the fragmentation/distortion issue resolved?")
    print("The new display should show clear, crisp text.")

if __name__ == "__main__":
    main()