#------------------------------------------------------------------------------
#Library

from __future__ import print_function
import csv
#from fmpy.util import plot_result
import RPi.GPIO as GPIO
from serial import Serial
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl

#------------------------------------------------------------------------------
#Graph Setup
fig=plt.figure()

mpl.rcParams["path.simplify"]=True

ax1=fig.add_subplot(221)
ax1.set_title("Bottom Temp")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Temp ('C)")

ax2=fig.add_subplot(222)
ax2.set_title("Top Temp")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Temp ('C)")

ax3=fig.add_subplot(223)
ax3.set_title("Bottom Volt")
ax3.set_xlabel("Time (s)")
ax3.set_ylabel("Volt (V)")

ax4=fig.add_subplot(224)
ax4.set_title("Top Volt")
ax4.set_xlabel("Time (s)")
ax4.set_ylabel("Volt (V)")

line1,=ax1.plot([],[],lw=2,color="r")
line2,=ax2.plot([],[],lw=2,color="r")
line3,=ax3.plot([],[],lw=2,color="g")
line4,=ax4.plot([],[],lw=2,color="g")
line=[line1,line2,line3,line4]

for ax in [ax1,ax2]:
    ax.set_ylim(0,220)
    ax.set_xlim(0,1000)
    ax.grid()

for ax in [ax1,ax2]:
    ax.set_ylim(-1,6)
    ax.set_xlim(0,1000)
    ax.grid()
    


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
    Hope=180
    try:
        while True:
            start=time.time()
            Temp1, Temp2=Ardread()
            
            if Temp1<Hope:
                if Hope-Temp1>100:
                    pwmvalue1=99
                elif Hope-Temp1<=100 and Hope-Temp1>60:
                    pwmvalue1=50
                elif Hope-Temp1<=50 and Hope-Temp1>30:
                    pwmvalue1=20
                elif Hope-Temp1<=30 and Hope-Temp1>10:
                    pwmvalue1=10
                elif Hope-Temp1<10:
                    pwmvalue1=5
            elif Temp1==Hope:
                pwmvalue1=1
            else:
                pwmvalue1=0
            volt1.append(pwmvalue1*0.0494)
                
            if Temp2<Hope:
                if Hope-Temp2>100:
                    pwmvalue2=99
                elif Hope-Temp2<=100 and Hope-Temp2>60:
                    pwmvalue2=50
                elif Hope-Temp2<=50 and Hope-Temp2>30:
                    pwmvalue2=20
                elif Hope-Temp2<=30 and Hope-Temp2>10:
                    pwmvalue2=10
                elif Hope-Temp2<10:
                    pwmvalue2=5
            elif Temp2==Hope:
                pwmvalue2=1
            else:
                pwmvalue2=0
            volt2.append(pwmvalue2*0.0494)
            
            print("pwmvalue1 : ",pwmvalue1)
            print("volt1 : ", volt1[-1])
            
            print("pwmvalue2 : ",pwmvalue2)
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
            ani=animation.FuncAnimation(fig,run,data_gen(timeV,Temp1,Temp2,volt1,volt2),blit=True,interval=1,repeat=False)
            fig.tight_layout()
            plt.show()
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
    if mega.readable():
        res=mega.readline()
        try:
            u=res[:-2].decode()
            print(u)
            if "T1p" in u:
                u1=float(u.lstrip("T1p"))
            elif "T2p" in u:
                u2=float(u.lstrip("T2p"))
            else:
                pass
        except:
            res=mega.readline()
            u=res[:-2].decode()
            if "T1p" in u:
                u1=float(u.lstrip("T1p"))
            elif "T2p" in u:
                u2=float(u.lstrip("T2p"))
            else:
                pass
    
    timesave.append(timeV)
    tempsave1.append(u1)
    tempsave2.append(u2)

    Temp1=u1
    Temp2=u2
    
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
    
def data_gen(t,T1,T2,v1,v2):
    yield t, T1, T2, v1, v2
    
def run():
    line[0].set_data(timesave,tempsave1)
    line[1].set_data(timesave,tempsave2)
    line[2].set_data(timesave,volt1)
    line[3].set_data(timesave,volt2)

#------------------------------------------------------------------------------
#main

if __name__=="__main__":
    pwmout()
