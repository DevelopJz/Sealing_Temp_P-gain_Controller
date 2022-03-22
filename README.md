# Python3 Project_1
## P-gain Controller with GUI

### 사용 언어
**Python 3.7.6**  
**Arduino 1.8.13**  

### 사용 환경
**Ubuntu 18.04 LTS**  

### 라이브러리
 - Python  
   - __future__  
   - csv  
   - RPI.GPIO
   - pyserial  
   - time  
   - matplotlib
   - tkinter  
 
 - Arduino  
   - max6675.h  

### 라이브러리 설치
**Python**  

```python

python -m pip install 라이브러리명

```

**Arduino**  

필요한 라이브러리 인터넷 검색 후 zip 파일 다운로드  

C:\Users\사용자명\Documents\Arduino\libraries 에 zip 파일 저장  

zip 파일 불러오기  
![image](https://user-images.githubusercontent.com/96412126/159386813-feac94ca-6859-458a-b36c-97582c2fd0cd.png)

C:\Users\사용자명\Documents\Arduino\libraries 에서 다운로드한 zip 파일 선택  

### 동작 개요

Jetson Nano : Temp / Input Volt 기록 및 Temp 그래프 저장, PWM 신호 발생  
arduino : Heater의 온도 값 수신, PWM 신호 수신하여 Heater에 전압 인가  
MAX6675 : K-Type 열전대 센서, Heater의 온도 값 Arduino에 전달  
Heater : 0~5V 전압으로 동작, 목표 온도 180 °C  

![image](https://user-images.githubusercontent.com/96412126/159418253-2f38adf1-9233-45af-8753-3ecac418b3da.png)

### 코드 설명  

**Ar_GPIO.ino**  

Jetson Nano에서 PWM 값 읽어 Analog Volt 값으로 환산하여 Heater에 전압 인가
MAX6675를 통해 히터에서 온도 값 받아 Jetson Nano에 전달

****  



