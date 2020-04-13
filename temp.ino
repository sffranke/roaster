#include <max6675.h>
#include <ModbusRtu.h>

// data array for modbus network sharing
uint16_t au16data[16] = {
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1 };

/**
 *  Modbus object declaration
 *  u8id : node id = 0 for master, = 1..247 for slave
 *  u8serno : serial port (use 0 for Serial)
 *  u8txenpin : 0 for RS-232 and USB-FTDI 
 *               or any pin number > 1 for RS-485
 */
Modbus slave(1,0,0); // this is slave @1 and RS-232 or USB-FTDI

/*
int thermoDO = 4;
int thermoCS = 5;
int thermoCLK = 6;
*/

int thermoSO = 4;
int thermoCS = 5;
int thermoSCK = 6;

int temp;

int DELTA = 35; // 35°C differance the messured temperature to the real temperature of the beans.
// MAX6675 thermocouple(thermoCLK, thermoCS, thermoDO);
MAX6675 thermocouple(thermoSCK, thermoCS, thermoSO);

int relay = 9;  
  
void setup() {
  slave.begin( 19200); // 19200 baud, 8-bits, even, 1-bit stop
  // use Arduino pins 
  pinMode(relay, OUTPUT);
  delay(500);
  
}

void loop() {
   //write current thermocouple value
   
   temp = (uint16_t) (thermocouple.readCelsius()-DELTA)*100;
 
   //au16data[2] = (uint16_t) thermocouple.readCelsius()*100;
   au16data[2] = temp;
   //Serial.println(temp);

   //poll modbus registers
   slave.poll( au16data, 16 );

   //write relay value using pwm
   analogWrite(relay, (au16data[4]/100.0)*255);
   delay(250);
}
