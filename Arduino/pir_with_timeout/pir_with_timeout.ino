/*
 * S_DETECTOR (white with back) D2
 * 
 */

const int PIN_S_DETECTOR  = 2;
const int PIN_ARDUINO_LED  = 13;

int  timeout;
unsigned long time_stamp;
unsigned long time_delta;
int PIR_STATE;


void setup() {  
    Serial.begin(115200);
    pinMode( PIN_ARDUINO_LED, OUTPUT) ;
    pinMode (PIN_S_DETECTOR, INPUT);
    delay(6000);  
    Serial.println("ready to work");

  timeout = 30; // seconds without activity
  time_stamp = 0;
  time_delta = 0;
  PIR_STATE = 0; // no detection

}

void loop() {

  if (digitalRead(PIN_S_DETECTOR)) {
    PIR_STATE = 1;
    time_stamp = millis();

    digitalWrite(PIN_ARDUINO_LED, HIGH);
    delay(10);
    digitalWrite(PIN_ARDUINO_LED, LOW);
    delay(10);
    digitalWrite(PIN_ARDUINO_LED, HIGH);
  }
  
 
  time_delta = millis() - time_stamp; 

  if ((time_delta >= (timeout *1000)) && (PIR_STATE == 1)) {
    PIR_STATE = 0;
    digitalWrite(PIN_ARDUINO_LED, LOW);
  }
  
}
