#------------------------------------------------------------------------------
#PWM, PID Library

from __future__ import print_function
import csv
#from fmpy.util import plot_result
import RPi.GPIO as GPIO
from serial import Serial
import time
#import multiprocessing as mp

#------------------------------------------------------------------------------
#GUI Library
import matplotlib.pyplot as plt
#from matplotlib import animation
import matplotlib as mpl
import matplotlib.style as mplstyle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter

#------------------------------------------------------------------------------
#PID Setting

prostart=time.time()
prevtime=time.time()

tkp=120.0
tki=10.0
tkd=0.001

tsettemp=180#-6.3

bkp=120.0
bki=10.0
bkd=0.001

bsettemp=180#-6.3

errorprev=0
pwmflag=0

statflag=0

def mapping(x,in_min,in_max,out_min,out_max):
    return (x-in_min)*(out_max-out_min)/(in_max-in_min)+out_min

#------------------------------------------------------------------------------
#Jetson nano PWM

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

timeV=0.001
timesave=[]
tempsave1=[]
tempsave2=[]
volt1=[]
volt2=[]

with open("input.csv","w",encoding="utf-8",newline="") as f:
    writer=csv.writer(f)
    writer.writerow(["time","u1","u2"])
    
with open("output.csv","w",encoding="utf-8") as o:
    writer=csv.writer(o)
    writer.writerow(["time","y1","y2"])

#------------------------------------------------------------------------------
#Arduino Serial

mega=Serial(port="/dev/ttyACM0",baudrate=9600,)

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
    
def PIDCal(settemp,t,kp,ki,kd):
    global pwmflag
    global errorprev
    
    error=settemp-t
    
    if error>10:
        PID=99
    else:
        pidvalue=round(kp*error+ki*error*(0.2)+kd*(error-errorprev)/(0.2),1)
        PID=mapping(pidvalue,0,415,38,99)
        PID=round(PID,0)
    
    if PID >= 100:
        PID=99
    elif PID < 0:
        PID=1

    if t>settemp:
        if pwmflag==0:
            PID=38
            pwmflag=1
        elif pwmflag==1:
            PID=38
            pwmflag=2
        elif pwmflag==2:
            PID=39
            pwmflag=0
    else:
        pass
    
    errorprev=error
    
    return PID

#------------------------------------------------------------------------------
#Main Code, PWM

def MAIN_code():
    global timeV
    global statflag
    global GI
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(other_pin, GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(output_pin, 100)
    q = GPIO.PWM(other_pin, 100)
    p.start(5)
    q.start(5)

    try:
        """
        Ftemp1, Ftemp2=Ardread()

        if Ftemp1>168 and Ftemp2>168:
            settemp=180+1.3
        else:
            pass
        """
        start=time.time()
        
        Temp1, Temp2=Ardread()
        
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
        
        PID1=PIDCal(tsettemp,Temp1,tkp,tki,tkd)
        PID2=PIDCal(bsettemp,Temp2,bkp,bki,bkd)
        
        volt1.append(PID1*0.05)
        volt2.append(PID2*0.05)
        
        t.append(GI)
        T1.append(Temp1)
        T2.append(Temp2)

        line1.set_data(t,T1)
        line2.set_data(t,T2)

        xmin,xmax=ax.get_xlim()
        if GI>xmax:
            ax.set_xlim(xmin+1,xmax+1)
            
        """fig.canvas.restore_region(axbackground)

        ax.draw_artist(line1)
        ax.draw_artist(line2)

        fig.canvas.blit(ax.bbox)"""
        fig.canvas.draw()
            
        fig.canvas.flush_events()
        
        print("Top Set : ",tsettemp)
        print("Temp1 : ",Temp1)
        print("pid1 : ",PID1)
        print("volt1 : ", round(volt1[-1],3))
        
        print("Bottom Set : ",bsettemp)
        print("Temp2 : ",Temp2)
        print("pid2 : ",PID2)
        print("volt2 : ", round(volt2[-1],3))
        
        p.ChangeDutyCycle(PID1)
        q.ChangeDutyCycle(PID2)
        
        end=time.time()
        print("time : ",round((end-start),4))
        timeV=round(timeV+(end-start),3)
        GI=timeV
        timesave.append(timeV)
        
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
#Tkinter GUI

t=[]
T1=[]
T2=[]
GI=0

def start_heat():
    global statflag
    consolelabel.config(text="Code Start")
    statusframe.config(bg="green")
    statuslabel.config(text="start", bg="green")
    statflag=0
    pass

def stop_heat():
    global statflag
    consolelabel.config(text="Code Stop")
    statusframe.config(bg="red")
    statuslabel.config(text="stop", bg="red")
    statflag=1
    pass

fig=plt.figure()

window = tkinter.Tk()
window.title("Sealing Test")
window.geometry("1024x720+100+100")
window.resizable(False,False)

graphframe=tkinter.Frame(window, relief="solid", bd=2)
graphframe.pack(side="right", fill="both", expand=True)

canvas=FigureCanvasTkAgg(fig, master=graphframe) #
canvas.get_tk_widget().pack(fill="both", expand=True)

#mpl.use("GTK3Agg")
mpl.rcParams['path.simplify']=True
mpl.rcParams['path.simplify_threshold']=1.0
mpl.rcParams['agg.path.chunksize']=10000
mplstyle.use('fast')

ax=fig.add_subplot()

line1,=ax.plot([],lw=2,color="b")
line2,=ax.plot([],lw=2,color="g")

ax.set_xlabel("Time (s)")
ax.set_ylabel("Temp ('C)")
ax.set_title("Temp Graph")
ax.grid(True)

ax.set_xlim([0,600])
ax.set_ylim([0,250])

"""
fig.canvas.draw()
plt.show()

axbackground=fig.canvas.copy_from_bbox(plt.bbox)
"""


consoleframe=tkinter.Frame(graphframe, relief="solid", bd=2, bg="white")
consoleframe.pack(side="bottom", fill="both", expand=False)

fileframe=tkinter.Frame(consoleframe, relief="solid", bd=2)
fileframe.pack(side="top", fill="both", expand=False)

def findfile():
       fileframe.filename=tkinter.filedialog.askopenfilename(initialdir="/home/ivh/Downloads", title="Choose Your File", filetypes=(("fmu file", "*.fmu"),))
       filelabel_2.config(text=fileframe.filename)
       consolelabel.config(text="Load file")

filebutton=tkinter.Button(fileframe, text="Open", width=15, command=findfile)
filebutton.grid(row=1, column=0)

filelabel_1=tkinter.Label(fileframe,text="File : ")
filelabel_1.grid(row=1, column=1)
       
filelabel_2=tkinter.Label(fileframe,text="File Name Here")
filelabel_2.grid(row=1, column=2)
       
consolelabel=tkinter.Label(consoleframe,text="something wrong, print here", bg="white")
consolelabel.pack(anchor="w", expand=False)

actframe=tkinter.Frame(window, relief="solid", bd=2)
actframe.pack(side="top", fill="both", expand=True)

statusframe=tkinter.Frame(actframe, relief="solid", bg="green")
statusframe.pack(side="bottom", fill="both", expand=True)

statuslabel=tkinter.Label(statusframe,text="start", bg="green")
statuslabel.pack(expand=True)

actlabel=tkinter.Label(actframe,text="코드 동작")
actlabel.pack()

actbutton_1=tkinter.Button(actframe, text="Start", width=15, command=start_heat)
actbutton_1.pack()

actbutton_2=tkinter.Button(actframe, text="Stop", width=15, command=stop_heat)
actbutton_2.pack()


controlframe=tkinter.Frame(window, relief="solid", bd=2)
controlframe.pack(side="bottom", fill="both", expand=True)

controllabel=tkinter.Label(controlframe,text="코드 제어")
controllabel.pack()


topframe=tkinter.Frame(controlframe, relief="solid", bd=2)
topframe.pack(side="top",fill="both",expand=True)

topvar=tkinter.DoubleVar()

def topselect(t):
       topscale.set(t)
    
toplabel1=tkinter.Label(topframe, text="Heating Plate Top ('C)")
toplabel1.pack()

topscale=tkinter.Scale(topframe, variable=topvar, relief="sunken", command=topselect, orient="horizontal", showvalue=True, resolution=0.01, digit=3, to=tsettemp+5, length=200)
topscale.pack()

toplabel2=tkinter.Label(topframe, text="Set Temp ('c)")
toplabel2.pack(anchor="w")

topspinbox1=tkinter.Spinbox(topframe, from_=1, to=240, validate="all", values=tsettemp)
topspinbox1.pack()

toplabel3=tkinter.Label(topframe, text="Kp")
toplabel3.pack(anchor="w")

topspinbox2=tkinter.Spinbox(topframe, validate="all", values=tkp)
topspinbox2.pack()

toplabel4=tkinter.Label(topframe, text="Ki")
toplabel4.pack(anchor="w")

topspinbox3=tkinter.Spinbox(topframe, validate="all", values=tki)
topspinbox3.pack()

toplabel5=tkinter.Label(topframe, text="Kd")
toplabel5.pack(anchor="w")

topspinbox4=tkinter.Spinbox(topframe, validate="all", values=tkd)
topspinbox4.pack()


bottomframe=tkinter.Frame(controlframe, relief="solid", bd=2)
bottomframe.pack(side="top",fill="both",expand=True)

bottomvar=tkinter.DoubleVar()

def bottomselect(t):
       bottomscale.set(t)

label5_1=tkinter.Label(bottomframe, text="Heating Plate Bottom ('C)")
label5_1.pack()

bottomscale=tkinter.Scale(bottomframe, variable=bottomvar, relief="sunken", command=bottomselect, orient="horizontal", showvalue=True, resolution=0.01, digit=3, to=bsettemp+5, length=200)
bottomscale.pack()

bottomlabel2=tkinter.Label(bottomframe, text="Set Temp ('c)")
bottomlabel2.pack(anchor="w")

bottomspinbox1=tkinter.Spinbox(bottomframe, from_=1, to=240, validate="all", values=bsettemp)

bottomspinbox1.pack()

bottomlabel3=tkinter.Label(bottomframe, text="Kp")
bottomlabel3.pack(anchor="w")

bottomspinbox2=tkinter.Spinbox(bottomframe, validate="all", values=bkp)
bottomspinbox2.pack()

bottomlabel4=tkinter.Label(bottomframe, text="Ki")
bottomlabel4.pack(anchor="w")

bottomspinbox3=tkinter.Spinbox(bottomframe, validate="all", values=bki)
bottomspinbox3.pack()

bottomlabel5=tkinter.Label(bottomframe, text="Kd")
bottomlabel5.pack(anchor="w")

bottomspinbox4=tkinter.Spinbox(bottomframe, validate="all", values=bkd)
bottomspinbox4.pack()


#------------------------------------------------------------------------------
#main


if __name__=="__main__":
    while True:
        if statflag==0:
            MAIN_code()
            window.update()
        elif statflag==1:
            window.update()
