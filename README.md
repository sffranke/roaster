# roaster
## Hardware
- Coffee Roaster (electrically heated pan with an arm that moves the beans)
- MAX6675 Thermoelement 
- Thermo Sensor 100mm Spade K-Typ Thermoelement (connected inside the body to the metal of the pan)
- Arduini Uno (or any other Arduino)
- SSR-40DA 40A Solid State Relay Input 3-32V DC Output 24-380V AC (did not have a smaller one, but works FINE)
  
## Software 
Artisan:
https://github.com/artisan-roaster-scope/artisan/releases/tag/v1.5.0

<img src="pics/artisan.jpeg"  width="300" height="200">
The slightly modified sketch from https://github.com/lukeinator42/coffee-roaster/blob/master/sketch/sketch.ino:

```
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
   au16data[2] = ((uint16_t) thermocouple.readCelsius()*100);

   //poll modbus registers
   slave.poll( au16data, 16 );

   //write relay value using pwm
   analogWrite(relay, (au16data[4]/100.0)*255);
   delay(500);
}
```
Using PID settings: P=7, I=0.14, D=94
<br>
<img src="pics/bohnengruen.jpg"  width="150" height="100">
<img src="pics/bohnenbraun.jpg"  width="150" height="100">
## Experiences
I usually rost 333 kg ( 1kg/3 :) ) at once and it takes 25-28 minutes, depending on the grade I want.
<img src="pics/set.jpg"  width="300" height="200">
