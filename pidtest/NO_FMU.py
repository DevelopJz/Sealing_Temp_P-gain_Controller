#------------------------------------------------------------------------------
#Library

from __future__ import print_function
import csv
#from fmpy.util import plot_result
import RPi.GPIO as GPIO
from serial import Serial
import time
import matplotlib.pyplot as plt

#------------------------------------------------------------------------------
#Jetson nano PWM 

#GPIO.setwarnings(False)

output_pins = {
        'JETSON_XAVIER': 18,
        'JETSON_NANO': 33,
        'JETSON_NX': 33,
        'CLARA_AGX_XAVIER': 18,
}
output_pin = output_pins.get(GPIO.model, None)
other_pins={'JETSON_NANO':32,}
other_pin = other_pins.get(GPIO.model, None)

if output_pin is None:
    raise Exception('PWM not supported on this board')
if other_pin is None:
    raise Exception('PWM not supported on this board')

#------------------------------------------------------------------------------
#Arduino Temp value

mega=Serial(port="/dev/ttyACM0",baudrate=9600,)

timeV=0
timesave=[]
tempsave1=[]
tempsave2=[]
volt1=[]
volt2=[]
plotx=[]
ploty=[]

with open("input.csv","w",encoding="utf-8",newline="") as f:
    writer=csv.writer(f)
    writer.writerow(["time","u1","u2"])
    
with open("output.csv","w",encoding="utf-8") as o:
    writer=csv.writer(o)
    writer.writerow(["time","y1","y2"])
    
#------------------------------------------------------------------------------
#Jetson nano PWM

def pwmout():
    global timeV
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(other_pin, GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(output_pin, 100)
    q = GPIO.PWM(other_pin, 100)
    p.start(5)
    q.start(5)
    Hope=180+8.2
    try:
        while True:
            start=time.time()
            #Temp1, Temp2=tempfunction()
            #tempgraph(timesave,tempsave1)
            Temp1, Temp2=Ardread()
            
            if Temp1<Hope:
                if Hope-Temp1>=4:
                    pwmvalue1=99
                elif Hope-Temp1<4:
                    pwmvalue1=60
            elif Temp1==Hope:
                pwmvalue1=50
            else:
                pwmvalue1=1
            volt1.append(pwmvalue1*0.05)
                
            if Temp2<Hope:
                if Hope-Temp2>=4:
                    pwmvalue2=99
                elif Hope-Temp2<4:
                    pwmvalue2=60
            elif Temp2==Hope:
                pwmvalue2=50
            else:
                pwmvalue2=1
            volt2.append(pwmvalue2*0.05)
            
            print("Temp1 : ",Temp1)
            print("Temp2 : ",Temp2)
            
            print("pwmvalue1 : ",pwmvalue1)
            print("pwmvalue2 : ",pwmvalue2)
            
            print("volt1 : ", volt1[-1])
            print("volt2 : ", volt2[-1])
            
            if pwmvalue1 > 100:
                pwmvalue1=100
            elif pwmvalue1 < 0:
                pwmvalue1=1
                
            if pwmvalue2 > 100:
                pwmvalue2=100
            elif pwmvalue2 < 0:
                pwmvalue2=1
            p.ChangeDutyCycle(pwmvalue1)
            q.ChangeDutyCycle(pwmvalue2)
            end=time.time()
            print("time : ",end-start)
            timeV=round(timeV+(end-start),3)
        #plt.show()
    except KeyboardInterrupt:
        print("Ctrl+C")
        with open("input.csv","a",encoding="utf-8",newline="") as f:
            writer=csv.writer(f)
            i=0
            while len(timesave)!=i:
                writer.writerow([timesave[i],tempsave1[i],tempsave2[i]])
                i=i+1
        
        with open("output.csv","a",encoding="utf-8",newline="") as o:
            writer=csv.writer(o)
            j=0
            while len(timesave)!=j:
                writer.writerow([timesave[j],volt1[j],volt2[j]])
                j=j+1
    finally:
        p.stop()
        GPIO.cleanup()

#------------------------------------------------------------------------------
#FMU simulation

def tempfunction():
    #if mega.readable():
    res=mega.readline()
    try:
        u=float(res[:-2].decode())
    except:
        res=mega.readline()
        u=float(res[:-2].decode())
    print("temp : ",u)
    
    timesave.append(timeV)
    tempsave1.append(u)
    tempsave2.append(u)

    Temp1=u
    Temp2=u
    
    return Temp1, Temp2

def Decode(A):
    A=A.decode()
    t1=float(A[:6])
    t2=float(A[7:])
    return t1, t2
    
def Ardread():
    if mega.readable():
        res=mega.readline()
        code=Decode(res)
        return code
    else:
        print("Read Error (Ardread)")

#------------------------------------------------------------------------------
#Temp Graph
    
def tempgraph(t,inp):
    plotx.append(t[-1])
    ploty.append(inp[-1])
    
    plt.grid(True)
    plt.xlabel("Time")
    plt.ylabel("Temp")
    if t[-1]>50:
        plotx.pop(0)
        ploty.pop(0)
        plt.plot(plotx,ploty,"r")
    else:
        plt.plot(plotx,ploty,"r")
    """if len(plotx)>50:
        plt.plot(plotx[len(plotx)-50:],ploty[len(plotx)-50:],"r")
    else:
        plt.plot(plotx,ploty,"r")"""
    
    plt.pause(1e-100)


#------------------------------------------------------------------------------
#main

if __name__=="__main__":
    pwmout()
