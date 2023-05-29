#include <Wire.h>
#include <ps2.h>
#define SLAVE_ADDRESS 0x04
#define MOUSE_DATA 8
#define MOUSE_CLOCK 9

int volumePot = 3;
int treblePot = 2;
char mstat;
char mx;
char station;
int sw1 = 4;
int sw2 = 5;
int sw3 = 6;
int sw4 = 7;

typedef struct sensorData_t{
  byte treble;
  byte volume;
  byte station;
  byte rsw1;
  byte rsw2;
  byte rsw3;
  byte rsw4;
};

typedef union I2C_Packet_t{
 sensorData_t sensor;
 byte I2CPacket[sizeof(sensorData_t)];
};
I2C_Packet_t sempData;  

PS2 mouse(9, 8);

void setup() {
  Serial.begin(9600);
  Wire.begin(SLAVE_ADDRESS);
  Wire.onRequest(sendData);
  pinMode(sw1, INPUT_PULLUP);
  pinMode(sw2, INPUT_PULLUP);
  pinMode(sw3, INPUT_PULLUP);
  pinMode(sw4, INPUT_PULLUP);
  delay(100);
  mouse_init();
}

void loop() {
  readSensors();
  // DEBUG
  sendSerial();
  delay(1000);
}

void readSensors() {
  mouse.write(0xeb);
  mouse.read();
  mx = mouse.read();
  station = mouse.read();
  sempData.sensor.treble = map(analogRead(treblePot), 0, 1023, 9, 0);
  sempData.sensor.volume = map(analogRead(volumePot), 0, 1023, 100, 0);
  sempData.sensor.rsw1 = digitalRead(sw1);
  sempData.sensor.rsw2 = digitalRead(sw2);
  sempData.sensor.rsw3 = digitalRead(sw3);
  sempData.sensor.rsw4 = digitalRead(sw4);
  sempData.sensor.station = station, DEC;
}

void sendSerial() {
  Serial.println(" ");
  Serial.print("Treble: ");
  Serial.print(sempData.sensor.treble);
  Serial.println(" ");
  Serial.print("Volume: ");
  Serial.print(sempData.sensor.volume);
  Serial.println(" ");
  Serial.print("SW1: ");
  Serial.print(sempData.sensor.rsw1);
  Serial.println(" ");
  Serial.print("SW2: ");
  Serial.print(sempData.sensor.rsw2);
  Serial.println(" ");
  Serial.print("SW3: ");
  Serial.print(sempData.sensor.rsw3);
  Serial.println(" ");
  Serial.print("SW4: ");
  Serial.print(sempData.sensor.rsw4);
  Serial.println(" ");
  Serial.print("Mouse: ");
  Serial.print(sempData.sensor.station);
}

void mouse_init() {
  mouse.write(0xff);
  mouse.read();
  mouse.read();
  mouse.read();
  mouse.write(0xf0);
  mouse.read();
  delayMicroseconds(100);
}

void sendData(){
  Wire.write(sempData.I2CPacket, sizeof(sensorData_t));
}
