#include <ModbusRtu.h>

uint16_t au16data[16] = { 0 };
Modbus slave(1, Serial, 0);
const int ledPin = LED_BUILTIN;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(19200); 
  slave.start();
}

void loop() {
  slave.poll(au16data, 16);

  uint16_t uno_value = au16data[0];

  if (uno_value != 0) {
    digitalWrite(ledPin, HIGH);
  } else {
    digitalWrite(ledPin, LOW);
  }
}
