#include "max6675.h"

#define PWM_IN 10
#define VOLT_OUT 6

#define ts_SO 30
#define ts_CS 32
#define ts_SCK 34
#define TEMP_VOLT 7

MAX6675 ts(ts_SCK,ts_CS,ts_SO);

void setup() {
  pinMode(PWM_IN,INPUT);
  pinMode(VOLT_OUT,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  unsigned long sensorValue=pulseIn(PWM_IN,HIGH);
  if(sensorValue>10000) {
    sensorValue=10000;
  }
  int conv=map(sensorValue,0,10000,0,255);
  analogWrite(VOLT_OUT,conv);
  float volt=conv*0.0197078431;
  float temp=ts.readCelsius();
  Serial.println(temp);
  delay(100);
}
