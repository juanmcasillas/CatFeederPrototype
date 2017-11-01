// HCU TEST
// first test for the HCU (hardware control unit) of CatFeeder
// TEST THE PIR SENSOR
//
//
/*
 * PIN MAPPING
 * 
 * S_DETECTOR (white with back) D2
 * 
 */

const int PIN_S_DETECTOR  = 2;
const int PIN_ARDUINO_LED  = 13;

void setup()
   {  pinMode( PIN_ARDUINO_LED, OUTPUT) ;
      pinMode (PIN_S_DETECTOR, INPUT);
      delay(6000);
   }

void loop()
   {  if (digitalRead(PIN_S_DETECTOR))
          digitalWrite( PIN_ARDUINO_LED , HIGH);
      else
          digitalWrite( PIN_ARDUINO_LED , LOW);
      delay(100);
   }
 
