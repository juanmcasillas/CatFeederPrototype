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
 * DOOR_PWM_1_IN (white / brown)    D4
 * DOOR_DIRA_IN (brown)             D5             
 * DOOR_DIRB_IN (green)             D2
 * DOOR_RED_OUT                     motor_red
 * DOOR_BLACK_OUT                   motor_black
 * 
 * LED_DIRA_IN                      jumped to VCC_ARDUINO (red)
 * LED_DIRB_IN                      jumped to GND (black)
 * LED_RED_OUT (white)
 * LED_BLACK_OUT (red)
 * LED_PWM_2_IN (white/green)       D3
 * 
 * S_OPEN (green with black)    D7 
 * S_CLOSED (red with black)    D8
 * S_DETECTOR (white with back) D9
 * 
 */
const int PIN_DOOR_PWM_1_IN   = 4;
const int PIN_DOOR_DIRA_IN    = 5;                   
const int PIN_DOOR_DIRB_IN    = 2;

const int PIN_LED_PWM_2_IN    = 3;

const int PIN_S_OPEN      = A1;
const int PIN_S_CLOSED    = A0;
const int PIN_S_DETECTOR  = 9;

const int PIN_ARDUINO_LED  = 13;


int counter;
int door_open;
int door_closed;
int speed;

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


  counter = 0;
  speed = 0;
}



void loop() {
/*
 * DETECTOR TEST
 */
 /*
  data_s_detector = digitalRead(PIN_S_DETECTOR);
  if(data_s_detector == 1){ 
    digitalWrite(PIN_S_LED, HIGH);
  }
  else{
       digitalWrite(PIN_S_LED, LOW);
  }
  delay(10);
*/

/*
 * LED PWM TEST
 */
 /*
 if (counter < 255) {
  analogWrite(PIN_LED_PWM_2_IN, counter);
  counter +=1;
 }
 else {
  Serial.println("done");
  counter = 0;
  delay(1000);
 }
 delay(10);
 */
/*
 * DOOR SENSOR TEST
 */
 /*
  door_open = analogRead(PIN_S_OPEN);
  door_closed = analogRead(PIN_S_CLOSED);

  if (door_closed == 1023) {
    Serial.println("Door Closed");
  }
  else {
    if (door_open == 1023) { 
      Serial.println("Door Open");
    }
  }
  delay(1000);
  */
  /*
   * DOOR MOTORS
   */

    digitalWrite(PIN_DOOR_DIRA_IN,LOW);
    digitalWrite(PIN_DOOR_DIRB_IN,LOW);

 /* open door */
 Serial.println("open door");
 for (int i=0; i<100; i++) {
    analogWrite(PIN_DOOR_PWM_1_IN, 100+i);
    digitalWrite(PIN_DOOR_DIRA_IN,HIGH);
    digitalWrite(PIN_DOOR_DIRB_IN,LOW);
    delay(100);
  }

 /* close door */
 Serial.println("close door");
  for (int i=0; i<100; i++) {
    analogWrite(PIN_DOOR_PWM_1_IN, 100+i);
    digitalWrite(PIN_DOOR_DIRA_IN,LOW);
    digitalWrite(PIN_DOOR_DIRB_IN,HIGH);
    delay(100);
  }
  
    digitalWrite(PIN_DOOR_DIRA_IN,LOW);
    digitalWrite(PIN_DOOR_DIRB_IN,LOW);
   

  
}



