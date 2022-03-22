#include "max6675.h"

#define PWM_IN 10
#define VOLT_OUT 6

#define ts_SO 30
#define ts_CS 32
#define ts_SCK 34
#define TEMP_VOLT 7

MAX6675 ts(ts_SCK,ts_CS,ts_SO);

void setup() {
  // put your setup code here, to run once:
  pinMode(PWM_IN,INPUT);
  pinMode(VOLT_OUT,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  unsigned long sensorValue=pulseIn(PWM_IN,HIGH);
  if(sensorValue>10000) {
    sensorValue=10000;
  }
  //Serial.println(sensorValue);
  int conv=map(sensorValue,0,10000,0,255);
  //Serial.println(conv);
  analogWrite(VOLT_OUT,conv);
  float volt=conv*0.0197078431;
  
  //Serial.print("OutVoltage : ");
  //Serial.print(volt);
  //Serial.println(" V");

  float temp=ts.readCelsius();
  Serial.println(temp);
  //Serial.print("Temp : ");
  //Serial.print(temp);
  //Serial.println(" 'C");
  
  //if(temp<255) {
    //int tempvolt=map(temp,0,1023,0,169);
    //analogWrite(TEMP_VOLT,tempvolt);
    //Serial.print("InVoltage : ");
    //Serial.print(tempvolt*0.0197078431);
    //Serial.println(" V");
  //}
  delay(100);
}
