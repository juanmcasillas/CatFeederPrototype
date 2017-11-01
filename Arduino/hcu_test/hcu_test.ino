// HCU TEST
// first test for the HCU (hardware control unit) of CatFeeder
//
//
/*
 * PIN MAPPING
 * 
 * ARDUINO_GND (green)          PIN2 right GND (arduino USB connecto down)
 * ARDUINO_VCC (red)            PIN4 right 5V
 * 
 * S_OPEN (green with black)    D2  
 * S_CLOSED (red with black)    D3
 * S_DETECTOR (white with back) A0 (for isolating spaces)
 * 
 */

const int PIN_S_OPEN      = 2;
const int PIN_S_CLOSED    = 3;
const int PIN_S_DETECTOR  = 5;

const int PIN_S_LED  = 13;

int  data_s_detector;

void setup() {
  Serial.begin(115200);
  //Serial.begin(9600);
  pinMode (PIN_S_DETECTOR, INPUT); 
  pinMode (PIN_S_LED, OUTPUT); 

}

void loop() {
  data_s_detector = digitalRead(PIN_S_DETECTOR);
  if(data_s_detector == 1){ 
    digitalWrite(PIN_S_LED, HIGH);
  }
  else{
    // nothing detected
     //Serial.println("nothing"); 
       digitalWrite(PIN_S_LED, LOW);
  }
  delay(10);
}



