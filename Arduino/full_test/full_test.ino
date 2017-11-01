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
 * DOOR_PWM_1_IN (white / brown)    D6
 * DOOR_DIRA_IN (brown)             D7             
 * DOOR_DIRB_IN (green)             D4
 * DOOR_RED_OUT                     motor_red
 * DOOR_BLACK_OUT                   motor_black
 * 
 * LED_DIRA_IN                      jumped to VCC_ARDUINO (red)
 * LED_DIRB_IN                      jumped to GND (black)
 * LED_RED_OUT (white)
 * LED_BLACK_OUT (red)
 * LED_PWM_2_IN (white/green)       D5
 * 
 * S_OPEN (green with black)        A1 
 * S_CLOSED (red with black)        A0
 * S_DETECTOR (white with back)     D2
 * 
 * PIR http://www.instructables.com/id/PIR-Motion-Sensor-Tutorial/
 */
const int PIN_DOOR_PWM_1_IN   = 6;
const int PIN_DOOR_DIRA_IN    = 7;                   
const int PIN_DOOR_DIRB_IN    = 4;

const int PIN_LED_PWM_2_IN    = 5;

const int PIN_S_OPEN      = A1;
const int PIN_S_CLOSED    = A0;
const int PIN_S_DETECTOR  = 2;

const int PIN_ARDUINO_LED  = 13;


int door_open;
int door_closed;
int detector;


void setup() {
  Serial.begin(115200);
  //Serial.begin(9600);

  pinMode(PIN_DOOR_PWM_1_IN, OUTPUT);
  pinMode(PIN_DOOR_DIRA_IN, OUTPUT);          
  pinMode(PIN_DOOR_DIRB_IN, OUTPUT);
  pinMode(PIN_LED_PWM_2_IN, OUTPUT);

  pinMode(PIN_S_CLOSED, INPUT);
  pinMode(PIN_S_OPEN,INPUT);  
  pinMode(PIN_S_DETECTOR,INPUT);
  pinMode (PIN_ARDUINO_LED, OUTPUT); 
  
  detector = 0;
  door_open = 0;
  door_closed = 0;
}



void loop() {

  // start with door closed, please.

  door_open = analogRead(PIN_S_OPEN);
  door_closed = analogRead(PIN_S_CLOSED);
  detector = digitalRead(PIN_S_DETECTOR);

  if (detector) {
     digitalWrite(PIN_ARDUINO_LED, LOW);

        /* led test */
      for (int i=0; i< 255; i++) {
        analogWrite(PIN_LED_PWM_2_IN, i);
        delay(1);
      }
  

     
    if (door_closed == 1023) {
      Serial.println("Door Closed");
    }
    else {
      if (door_open == 1023) { 
        Serial.println("Door Open");
      }
    }
  

  
    /* open door */
    for (int i=0; i<255-100; i++) {
      analogWrite(PIN_DOOR_PWM_1_IN, 100+i);
      digitalWrite(PIN_DOOR_DIRA_IN,HIGH);
      digitalWrite(PIN_DOOR_DIRB_IN,LOW);
      delay(7);
    }
    
    digitalWrite(PIN_DOOR_DIRA_IN,LOW);
    digitalWrite(PIN_DOOR_DIRB_IN,LOW);
    delay(1000);
   /* close door */
  
    for (int i=0; i<255-80; i++) {
      analogWrite(PIN_DOOR_PWM_1_IN, 100+i);
      digitalWrite(PIN_DOOR_DIRA_IN,LOW);
      digitalWrite(PIN_DOOR_DIRB_IN,HIGH);
    delay(7);
    }
    
    digitalWrite(PIN_DOOR_DIRA_IN,LOW);
    digitalWrite(PIN_DOOR_DIRB_IN,LOW);
  
    /* stop light */
    analogWrite(PIN_LED_PWM_2_IN, LOW);

   
   delay(1000);  
  }
  else { 
    digitalWrite(PIN_ARDUINO_LED, HIGH);
  }
  delay(100);
   
}

