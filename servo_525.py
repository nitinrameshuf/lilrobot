#include <Servo.h>

Servo myServo;
int servoPin = 7;

void setup() {
    Serial.begin(9600);
    myServo.attach(servoPin);
    Serial.println("Enter angle (0-180):");
}

void loop() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');  
        input.trim();  

        if (input.length() == 0) {
            return;
        }

        int angle = input.toInt();  

        if (angle >= 0 && angle <= 180) {
            if (angle == 0) {
                Serial.println("Fine-tuning 0-degree position...");
                myServo.writeMicroseconds(525);  // Adjust 500-700 for proper zero position
            } else {
                int pulseWidth = map(angle, 0, 180, 500, 2500); // Map angle to MG996R range
                myServo.writeMicroseconds(pulseWidth);
            }

            Serial.print("Servo moved to: ");
            Serial.print(angle);
            Serial.println(" degrees");
        } else {
            Serial.println("Invalid angle! Enter a value between 0 and 180.");
        }
        Serial.println("Enter next angle:");
    }
}
