//RST           D9
//SDA(SS)      D10
//MOSI         D11
//MISO         D12
//SCK          D13

 //https://github.com/miguelbalboa/rfid/tree/master
 
#include <SPI.h>
#include <MFRC522.h>
 
const int RST_PIN = 5;            // Pin 9 para el reset del RC522
const int SS_PIN = 53;            // Pin 10 para el SS (SDA) del RC522
MFRC522 mfrc522(SS_PIN, RST_PIN);   // Crear instancia del MFRC522
 
void printArray(byte *buffer, byte bufferSize) {
   for (byte i = 0; i < bufferSize; i++) {
      Serial.print(buffer[i] < 0x10 ? " 0" : " ");
      Serial.print(buffer[i], HEX);
   }
}
 
void setup()
{
   Serial.begin(9600);      //Inicializa la velocidad de Serial
   SPI.begin();         //Función que inicializa SPI
   mfrc522.PCD_Init();     //Función  que inicializa RFID
   Serial.print("card reader init\n");
}
 
void loop()
{
   // Detectar tarjeta
   if (mfrc522.PICC_IsNewCardPresent())
   {
g
      if (mfrc522.PICC_ReadCardSerial())
      {
         Serial.print(F("Card UID:"));
         printArray(mfrc522.uid.uidByte, mfrc522.uid.size);
         Serial.println();
 
         // Finalizar lectura actual
         mfrc522.PICC_HaltA();
      }
   }
   delay(100);
}
