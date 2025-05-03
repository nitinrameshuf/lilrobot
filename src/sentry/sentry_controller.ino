/*
Sentry Controller V1
Dev: Nitin Ramesh
Date: 02 May 2025
*/

const int StatusPin = 5;
const int servotest1 =  17;
const int servotest2 =  41;
const int servotest3 =  45;
const int servotest4 =  2;
const int servotest5 =  1;
const int inputPin = 43;

void setup() {
  pinMode(StatusPin,OUTPUT);
  pinMode(servotest1,OUTPUT);
  pinMode(servotest2,OUTPUT);
  pinMode(servotest3,OUTPUT);
  pinMode(servotest4,OUTPUT);
  pinMode(servotest5,OUTPUT);
  pinMode(inputPin,INPUT);
  int status_mode = 1;

  Serial.begin(115200);
  while(!Serial);
}

void status_mode(int mode) {
  switch (mode) {
    case 1:
      digitalWrite(StatusPin,HIGH);
      break;
    case 2:
      digitalWrite(StatusPin,HIGH);
      delay(1000);
      digitalWrite(StatusPin,LOW);
      delay(1000);
    case 3:
      digitalWrite(StatusPin,LOW);
      break;
    default:
      break;
  }
}

void loop() {
  // 
  if(Serial.available()){
    char incomming = Serial.read();
    if(incomming == '1'){
      status_mode(1);
      digitalWrite(servotest1,LOW);
      digitalWrite(servotest2,LOW);
      digitalWrite(servotest3,LOW);
      digitalWrite(servotest4,LOW);
      digitalWrite(servotest5,LOW);
    }
    if(incomming == '3'){
        status_mode(3);
        digitalWrite(servotest1,HIGH);
        digitalWrite(servotest2,HIGH);
        digitalWrite(servotest3,HIGH);
        digitalWrite(servotest4,HIGH);
        digitalWrite(servotest5,HIGH);
  }
  // Serial.println(digitalRead(inputPin));
  if (digitalRead(inputPin) == HIGH) {
    Serial.write('2');
    delay(100);
  }
}
}


