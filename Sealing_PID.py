#------------------------------------------------------------------------------
#PWM, PID, GUI Library

from __future__ import print_function
import csv
import RPi.GPIO as GPIO
from serial import Serial
import time
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.style as mplstyle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter
#from fmpy.util import plot_result

#------------------------------------------------------------------------------
#PID Setting

prostart=time.time()

tkp=55.0
tki=0.5
tkd=0.001

tsettemp=180

bkp=70.0
bki=0.5
bkd=0.001

bsettemp=180
errorprev=0
pwmflag=0

statflag=0

def mapping(x,in_min,in_max,out_min,out_max):
    return (x-in_min)*(out_max-out_min)/(in_max-in_min)+out_min

#------------------------------------------------------------------------------
#PIDCalculator

def PIDCal(settemp,t,kp,ki,kd,n):
    global pwmflag
    global errorprev

    error=settemp-t

    if t<settemp+1 and t>=settemp:
        if pwmflag==0:
            PID=n
            pwmflag=1
        elif pwmflag==1:
            PID=n
            pwmflag=2
        elif pwmflag==2:
            PID=n+1
            pwmflag=0

        if PID >= 100:
            PID=99
        elif PID < 0:
            PID=1
    elif t<settemp:
        if error>20:
            PID=99
        else:
            pidvalue=round(kp*error+ki*error*(0.2)+kd*(error-errorprev)/(0.2),1)
            #print(pidvalue)
            PID=mapping(pidvalue,0,1000,45,99)
            PID=round(PID,0)

        if PID >= 100:
            PID=99
        elif PID < 0:
            PID=1
    else:
        PID=20

    errorprev=error
    return PID

#------------------------------------------------------------------------------
#Arduino Temp value, csv Setting

timeV=0.001
TM=0.001
gt=0.001
timesave=[]
tempsave1=[]
tempsave2=[]
volt1=[]
volt2=[]

with open("./input.csv","w",encoding="utf-8",newline="") as f:
    writer=csv.writer(f)
    writer.writerow(["time","u1","u2"])

with open("./output.csv","w",encoding="utf-8") as o:
    writer=csv.writer(o)
    writer.writerow(["time","y1","y2"])

#------------------------------------------------------------------------------
#Arduino Serial

mega=Serial(port="/dev/ttyACM0",baudrate=9600,)

def Decode(A):
    A=A.decode()
    index=A.find("V")
    t1=float(A[:index])
    t2=float(A[index+1:])
    return t1, t2

def Ardread():
    if mega.readable():
        #mega.flushInput()
        res=mega.readline()
        code=Decode(res)
        return code
    else:
        print("Read Error (Ardread)")

#------------------------------------------------------------------------------
#RealTime Graph

t=[]
T1=[]
T2=[]
x_start=0
x_end=600

tappend=t.append
T1append=T1.append
T2append=T2.append

def Rgraph(Temp1,Temp2,TM):
    global gt
    global x_start,x_end
    tappend(gt)
    T1append(Temp1)
    T2append(Temp2)

    if timeV>x_end:
        x_start=x_start+(TM)
        x_end=x_end+(TM)
        axxlim(x_start,x_end)

    figdraw()

    line1data(t,T1)
    line2data(t,T2)
    axlegend(loc="upper left")

    figevent()
    gt=gt+(TM+0.15)

#------------------------------------------------------------------------------
#Jetson nano PWM Setting

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
#Main Code, PWM

def MAIN_code():
    global timeV
    global TM
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(other_pin, GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(output_pin, 100)
    q = GPIO.PWM(other_pin, 100)
    p.start(5)
    q.start(5)

    try:
        while True:
            TMS=time.time()
            if statflag==0:
                Temp1,Temp2=Ardread()
                
                topselect(Temp1)
        
                tsettemp=float(topspinbox1.get())
                tkp=float(topspinbox2.get())
                tki=float(topspinbox3.get())
                tkd=float(topspinbox4.get())
        
                bottomselect(Temp2)
        
                bsettemp=float(bottomspinbox1.get())
                bkp=float(bottomspinbox2.get())
                bki=float(bottomspinbox3.get())
                bkd=float(bottomspinbox4.get())
        
                tempsave1.append(Temp1)
                tempsave2.append(Temp2)
        
                PID1=PIDCal(tsettemp,Temp1,tkp,tki,tkd,40)
                PID2=PIDCal(bsettemp,Temp2,bkp,bki,bkd,40)
        
                volt1.append(PID1*0.05)
                volt2.append(PID2*0.05)
        
                consolelabelL1.config(text="UPPER Info")
                consolelabelR1.config(text="LOWER Info")
        
                consolelabelL2.config(text="Upper Temp : {}".format(Temp1))
                consolelabelR2.config(text="Lower Temp : {}".format(Temp2))
        
                consolelabelL3.config(text="Upper Volt : {}".format(round(volt1[-1],3)))
                consolelabelR3.config(text="Lower Volt : {}".format(round(volt2[-1],3)))
        
                p.ChangeDutyCycle(PID1)
                q.ChangeDutyCycle(PID2)
                
                time.sleep(0.2)
                
                timeV=timeV+(TM+0.15)
                timesave.append(timeV)
                
                window.update()
            elif statflag==1:
                window.update()
            TME=time.time()
            TM=round(TME-TMS,3)
            print("Time : ",TM)
            Rgraph(Temp1,Temp2,TM)
            
            window.update()
            

    except KeyboardInterrupt:
        print("Ctrl+C, Work Done")
        proend=time.time()
        sec=round((proend-prostart),4)
        mins=int(round(sec/60,0))
        secs=int(round(sec%60,0))
        print("work time (s) : ",str(sec)+"s")
        print("work time (m) : ",str(mins)+"m "+str(secs)+"s")

        with open("./input.csv","a",encoding="utf-8",newline="") as f:
            writer=csv.writer(f)
            i=0
            while len(timesave)!=i:
                writer.writerow([timesave[i],tempsave1[i],tempsave2[i]])
                i=i+1

        with open("./output.csv","a",encoding="utf-8",newline="") as o:
            writer=csv.writer(o)
            j=0
            while len(timesave)!=j:
                writer.writerow([timesave[j],volt1[j],volt2[j]])
                j=j+1
    finally:
        p.stop()
        q.stop()
        GPIO.cleanup()

#------------------------------------------------------------------------------
#Tkinter GUI

def start_heat():
    global statflag
    consolelabelL1.config(text="Upper Start")
    consolelabelR1.config(text="Lower Start")
    consolelabelL2.config(text="")
    consolelabelR2.config(text="")
    consolelabelL3.config(text="")
    consolelabelR3.config(text="")
    statusframe.config(bg="lawn green")
    statuslabel.config(text="START", bg="lawn green", font=("Arial", 42))
    statflag=0
    pass

def stop_heat():
    global statflag
    consolelabelL1.config(text="Upper Stop")
    consolelabelR1.config(text="Lower Stop")
    consolelabelL2.config(text="")
    consolelabelR2.config(text="")
    consolelabelL3.config(text="")
    consolelabelR3.config(text="")
    statusframe.config(bg="red")
    statuslabel.config(text="STOP", bg="red", font=("Arial", 50))
    statflag=1
    pass

fig=plt.figure()

window = tkinter.Tk()
window.title("Sealing Test")
window.overrideredirect(True)
"""
window.geometry("{0}x{1}+0+0".format(window.winfo_screenwidth(),
                window.winfo_screenheight()))
"""
window.geometry("1024x720+0+0")
window.resizable(False,False)

def savecsv():
    proend=time.time()
    sec=round((proend-prostart),4)
    mins=int(round(sec/60,0))
    secs=int(round(sec%60,0))

    print("work time (s) : ",str(sec)+"s")
    print("work time (m) : ",str(mins)+"m "+str(secs)+"s")

    with open("./input.csv","a",encoding="utf-8",newline="") as f:
        writer=csv.writer(f)
        i=0
        while len(timesave)!=i:
            writer.writerow([timesave[i],tempsave1[i],tempsave2[i]])
            i=i+1

    with open("./output.csv","a",encoding="utf-8",newline="") as o:
        writer=csv.writer(o)
        j=0
        while len(timesave)!=j:
            writer.writerow([timesave[j],volt1[j],volt2[j]])
            j=j+1

    time.sleep(3)
    window.destroy()


graphframe=tkinter.Frame(window, relief="solid", bd=2)
graphframe.pack(side="right", fill="both", expand=True)

canvas1=FigureCanvasTkAgg(fig, master=graphframe)
canvas1.get_tk_widget().pack(fill="both", expand=True)

mpl.rcParams['path.simplify']=True
mpl.rcParams['path.simplify_threshold']=1.0
mpl.rcParams['agg.path.chunksize']=10000
mplstyle.use('fast')

ax=fig.add_subplot()

line1,=ax.plot([],lw=2,color="b",label="Upper Temp")
line2,=ax.plot([],lw=2,color="g",label="Lower Temp")

line1data=line1.set_data
line2data=line2.set_data
axxlim=ax.set_xlim
figdraw=fig.canvas.draw
axlegend=ax.legend
figevent=fig.canvas.flush_events

ax.set_xlabel("Time (s)")
ax.set_ylabel("Temp ('C)")
ax.set_title("Temp Graph")
ax.grid(True)

ax.set_xlim([x_start,x_end])
ax.set_ylim([0,250])

consoleframe=tkinter.Frame(graphframe, relief="solid", bd=2, bg="black")
consoleframe.pack(side="bottom", fill="both", expand=False)

consoleframeL=tkinter.Frame(consoleframe,relief="solid",bd=2, bg="black")
consoleframeL.pack(side="left", fill="both", expand=True)

consolelabelL1=tkinter.Label(consoleframeL,text="UPPER Info",
                           bg="black", fg="white")
consolelabelL1.pack(anchor="w", expand=False)

consolelabelL2=tkinter.Label(consoleframeL,text="Upper Temp : ",
                           bg="black", fg="white")
consolelabelL2.pack(anchor="w", expand=False)

consolelabelL3=tkinter.Label(consoleframeL,text="Upper Volt : ",
                           bg="black", fg="white")
consolelabelL3.pack(anchor="w", expand=False)

consoleframeR=tkinter.Frame(consoleframe,relief="solid",bd=2, bg="black")
consoleframeR.pack(side="left", fill="both", expand=True)

consolelabelR1=tkinter.Label(consoleframeR,text="LOWER Info",
                           bg="black", fg="white")
consolelabelR1.pack(anchor="w", expand=False)

consolelabelR2=tkinter.Label(consoleframeR,text="Lower Temp : ",
                           bg="black", fg="white")
consolelabelR2.pack(anchor="w", expand=False)

consolelabelR3=tkinter.Label(consoleframeR,text="Lower Volt : ",
                           bg="black", fg="white")
consolelabelR3.pack(anchor="w", expand=False)


quitbutton=tkinter.Button(consoleframe,text="Quit and Save", command=savecsv,
                          height=3)
quitbutton.pack(side="right",expand=False)


actframe=tkinter.Frame(window, relief="solid", bd=2)
actframe.pack(side="top", fill="both", expand=True)

statusframe=tkinter.Frame(actframe, relief="solid", bg="lawn green")
statusframe.pack(side="bottom", fill="both", expand=True)

statuslabel=tkinter.Label(statusframe,text="START", bg="lawn green",
                          font=("Arial",42))
statuslabel.pack(expand=True)

actlabel=tkinter.Label(actframe,text="코드 동작")
actlabel.pack()

actbutton_1=tkinter.Button(actframe, text="START", width=15,
                           command=start_heat, font=120)
actbutton_1.pack()

actbutton_2=tkinter.Button(actframe, text="STOP", width=15,
                           command=stop_heat, font=120)
actbutton_2.pack()


controlframe=tkinter.Frame(window, relief="solid", bd=2)
controlframe.pack(side="bottom", fill="both", expand=True)

controllabel=tkinter.Label(controlframe,text="코드 제어")
controllabel.pack()


topframe=tkinter.Frame(controlframe, relief="solid", bd=2)
topframe.pack(side="top",fill="both",expand=True)

tscalevar=tkinter.DoubleVar()
topvar=tkinter.DoubleVar(value=str(tsettemp))
tkpvar=tkinter.DoubleVar(value=str(tkp))
tkivar=tkinter.DoubleVar(value=str(tki))
tkdvar=tkinter.DoubleVar(value=str(tkd))

def topselect(t):
       topscale.set(t)

toplabel1=tkinter.Label(topframe, text="Heating Plate Top ('C)")
toplabel1.pack()

topscale=tkinter.Scale(topframe, variable=tscalevar, relief="sunken",
                       command=topselect, orient="horizontal",
                       showvalue=True, resolution=0.01, digit=3,
                       to=250, length=200)
topscale.pack()

toplabel2=tkinter.Label(topframe, text="Set Temp ('c)")
toplabel2.pack(anchor="w")

topspinbox1=tkinter.Spinbox(topframe, from_=1, to=240, validate="all", increment=1.0, textvariable=topvar)
topspinbox1.pack()

toplabel3=tkinter.Label(topframe, text="Kp")
toplabel3.pack(anchor="w")

topspinbox2=tkinter.Spinbox(topframe, from_=0, to=500, validate="all", increment=0.5, textvariable=tkpvar)
topspinbox2.pack()

toplabel4=tkinter.Label(topframe, text="Ki")
toplabel4.pack(anchor="w")

topspinbox3=tkinter.Spinbox(topframe, from_=0, to=20, validate="all", increment=0.1, textvariable=tkivar)
topspinbox3.pack()

toplabel5=tkinter.Label(topframe, text="Kd")
toplabel5.pack(anchor="w")

topspinbox4=tkinter.Spinbox(topframe, from_=0, to=10, validate="all", increment=0.001, textvariable=tkdvar)
topspinbox4.pack()


bottomframe=tkinter.Frame(controlframe, relief="solid", bd=2)
bottomframe.pack(side="top",fill="both",expand=True)

bscalevar=tkinter.DoubleVar()
bottomvar=tkinter.DoubleVar(value=str(bsettemp))
bkpvar=tkinter.DoubleVar(value=str(bkp))
bkivar=tkinter.DoubleVar(value=str(bki))
bkdvar=tkinter.DoubleVar(value=str(bkd))

def bottomselect(t):
       bottomscale.set(t)

label5_1=tkinter.Label(bottomframe, text="Heating Plate Bottom ('C)")
label5_1.pack()

bottomscale=tkinter.Scale(bottomframe, variable=bscalevar, relief="sunken",
                          command=bottomselect, orient="horizontal",
                          showvalue=True, resolution=0.01,
                          digit=3, to=250, length=200)
bottomscale.pack()

bottomlabel2=tkinter.Label(bottomframe, text="Set Temp ('c)")
bottomlabel2.pack(anchor="w")

bottomspinbox1=tkinter.Spinbox(bottomframe, from_=1, to=240, validate="all", increment=1.0, textvariable=bottomvar)

bottomspinbox1.pack()

bottomlabel3=tkinter.Label(bottomframe, text="Kp")
bottomlabel3.pack(anchor="w")

bottomspinbox2=tkinter.Spinbox(bottomframe, from_=0, to=500, validate="all", increment=0.5, textvariable=bkpvar)
bottomspinbox2.pack()

bottomlabel4=tkinter.Label(bottomframe, text="Ki")
bottomlabel4.pack(anchor="w")

bottomspinbox3=tkinter.Spinbox(bottomframe, from_=0, to=20, validate="all", increment=0.1, textvariable=bkivar)
bottomspinbox3.pack()

bottomlabel5=tkinter.Label(bottomframe, text="Kd")
bottomlabel5.pack(anchor="w")

bottomspinbox4=tkinter.Spinbox(bottomframe, from_=0, to=10, validate="all", increment=0.001, textvariable=bkdvar)
bottomspinbox4.pack()

#------------------------------------------------------------------------------
#main

if __name__=="__main__":
    MAIN_code()
