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

Jetson Nano : Temp / Input Volt 기록 및 PWM 신호 발생  
arduino : Heater의 온도 값 수신, PWM 신호 수신하여 Heater에 전압 인가  
MAX6675 : K-Type 열전대 센서, Heater의 온도 값 Arduino에 전달  
Heater : 0~5V 전압으로 동작, 목표 온도 180 °C, 상하 2개 Heater  

![image](https://user-images.githubusercontent.com/96412126/159418253-2f38adf1-9233-45af-8753-3ecac418b3da.png)

### 코드 설명  

**Ar_GPIO.ino**  

Jetson Nano에서 PWM 값 읽어 Analog Volt 값으로 환산하여 Heater에 전압 인가  
MAX6675를 통해 히터에서 온도 값 받아 Jetson Nano에 전달  

**Sealing_PID.py**  

Arduino에서 전달받는 온도 값 읽고 GUI에 시간에 따른 온도 그래프 출력  
받은 온도 값과 목표 온도 값의 차이만큼 PID 값 변화시켜 Arduino에 PWM 값 전달
input.csv (시간, 온도) / output.csv (시간, 전압) 기록  

**Sealing_PID_GUI**  
![image](https://user-images.githubusercontent.com/96412126/162860422-ed2221d7-bbfc-4f83-880b-9b382bd6de62.png)

**MakeGraph.py**  

Heater_PID.py에서 만들어진 input.csv로 시간에 따른 온도 그래프 작성

**Sealing_PID_graph**  
![image](https://user-images.githubusercontent.com/96412126/162860587-e88fe7be-57bb-4fe8-8eda-d41db79f5703.png)
