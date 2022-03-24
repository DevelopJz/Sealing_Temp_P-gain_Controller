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
#PID Setting

prostart=time.time()

kp=120.0
ki=10.0
kd=0.001

settemp=180#-6.3
prevtime=time.time()
errorprev1=0
error1=0

errorprev2=0
error2=0

def mapping(x,in_min,in_max,out_min,out_max):
    return (x-in_min)*(out_max-out_min)/(in_max-in_min)+out_min

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

timeV=0.001
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
    global errorprev1
    global errorprev2
    global settemp
    pwmflag=0
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(other_pin, GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(output_pin, 100)
    q = GPIO.PWM(other_pin, 100)
    p.start(5)
    q.start(5)
    try:
        Ftemp1, Ftemp2=Ardread()

        if Ftemp1>168 and Ftemp2>168:
            settemp=180+1.3
        else:
            pass
        
        while True:
            start=time.time()

            #tempgraph(timesave,tempsave1)
            Temp1, Temp2=Ardread()
            
            tempsave1.append(Temp1)
            tempsave2.append(Temp2)
            
            error1=settemp-Temp1
            error2=settemp-Temp2
            
            if error1>10:
                PID1=99
            else:
                pidvalue1=round(kp*error1+ki*error1*(0.2)+kd*(error1-errorprev1)/(0.2),1)
                PID1=mapping(pidvalue1,0,415,38,99)
                PID1=round(PID1,0)
                
            if error2>10:
                PID2=99
            else:
                pidvalue2=round(kp*error2+ki*error2*(0.2)+kd*(error2-errorprev2)/(0.2),1)
                PID2=mapping(pidvalue2,0,415,38,99)
                PID2=round(PID2,0)
            
            if PID1 >= 100:
                PID1=99
            elif PID1 < 0:
                PID1=1
                
            if PID2 >= 100:
                PID2=99
            elif PID2 < 0:
                PID2=1
                
            if Temp1>settemp and Temp2>settemp:
                settemp=180
                if pwmflag==0:
                    PID1=38
                    PID2=38
                    pwmflag=1
                elif pwmflag==1:
                    PID1=38
                    PID2=38
                    pwmflag=2
                elif pwmflag==2:
                    PID1=39
                    PID2=39
                    pwmflag=0
            elif Temp1>settemp and Temp2<settemp:
                if pwmflag==0:
                    PID1=38
                    pwmflag=1
                elif pwmflag==1:
                    PID1=38
                    pwmflag=2
                elif pwmflag==2:
                    PID1=39
                    pwmflag=0
            elif Temp1<settemp and Temp2>settemp:
                if pwmflag==0:
                    PID2=38
                    pwmflag=1
                elif pwmflag==1:
                    PID2=38
                    pwmflag=0
                elif pwmflag==2:
                    PID2=39
                    pwmflag=0
            else:
                pass
                
            volt1.append(PID1*0.05)
            volt2.append(PID2*0.05)
            
            print("settemp : ",settemp)
            print("Temp1 : ",Temp1)
            print("Temp2 : ",Temp2)
            #print("pidvalue1 : ",pidvalue1)
            #print("pidvalue2 : ",pidvalue2)
            print("pid1 : ",PID1)
            print("pid2 : ",PID2)
            print("volt1 : ", round(volt1[-1],3))
            print("volt2 : ", round(volt2[-1],3))
            
            p.ChangeDutyCycle(PID1)
            q.ChangeDutyCycle(PID2)
            errorprev1=error1
            errorprev2=error2
            end=time.time()
            print("time : ",round((end-start),4))
            timeV=round(timeV+(end-start),3)
            timesave.append(timeV)
        #plt.show()
    except KeyboardInterrupt:
        print("Ctrl+C, Work Done")
        proend=time.time()
        sec=round((proend-prostart),4)
        mins=int(round(sec/60,0))
        secs=int(round(sec%60,0))
        print("work time (s) : ",str(sec)+"s")
        print("work time (m) : ",str(mins)+"m "+str(secs)+"s")
        
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
    #print("temp : ",u)
    
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
