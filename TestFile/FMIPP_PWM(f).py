#------------------------------------------------------------------------------
#Library

from __future__ import print_function
import csv
import numpy as np
import fmpy as fm
import fmipp
#from fmpy.util import plot_result
import RPi.GPIO as GPIO
from serial import Serial
import sys
import time

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
if output_pin is None:
    raise Exception('PWM not supported on this board')

#------------------------------------------------------------------------------
#Arduino Temp value

mega=Serial(port="/dev/ttyACM0",baudrate=9600,)

timeV=0.0
print(type(timeV))

with open("input.csv","w",encoding="utf-8",newline="") as f:
    writer=csv.writer(f)
    writer.writerow(["time","u"])
    
with open("output.csv","w",encoding="utf-8") as o:
    writer=csv.writer(o)
    writer.writerow(["time","y"])

#------------------------------------------------------------------------------
#FMU INFO

timesave=[]
tempsave=[]
dt=np.dtype([("time","<f8"),("u","<f8")])

infolist=[]
repllist=[]
ndellist=[]
finallist=[]

delversion="FMIVersion"
deltype="FMIType"
delname="ModelName"
delstop="StopTime"
deltol="Tolerance"
delinput="uinput"
repoutput="output"

fmu="/home/pi/Downloads/FMU_File/MP_HW_TEST_CS_02.fmu"

f=open("fmu_info.txt","w",encoding="utf-8")
stdout=sys.stdout
sys.stdout=f
fm.dump(fmu)
f.close()
sys.stdout=stdout

with open("/home/pi/Downloads/FMU_File/fmu_info.txt","r",encoding="utf-8") as t:
    for i in range(0,24):
        line=t.readline()
        infolist.append(line)

for j in range(len(infolist)):
    repllist.append(infolist[j].replace(" ",""))
    ndellist.append(repllist[j].replace("\n",""))
    ndellist=[v for v in ndellist if v]

del ndellist[0]
del ndellist[3:11]
del ndellist[5:7]

finallist.append(ndellist[0].replace(delversion,""))
finallist.append(ndellist[1].replace(deltype,""))
finallist.append(ndellist[2].replace(delname,""))
finallist.append(ndellist[3].replace(delstop,""))
finallist.append(ndellist[4].replace(deltol,""))
finallist.append(ndellist[5].replace(delinput,""))
finallist.append(ndellist[6].replace(repoutput,""))

fmiversion=finallist[0]
fmitype=finallist[1]
fmu="/home/pi/Downloads/FMU_File/"+finallist[2]+".fmu"
stoptime=float(finallist[3])
tol=float(finallist[4])
starttime=float(finallist[5])
outval=finallist[6]

#------------------------------------------------------------------------------
#FMIPP Setting
logging_on=False
stop_before_event=False
event_search_precision=1e-10
integrator_type=fmipp.bdf
fmippfmu=fmipp.IncrementalFMU(fmu,logging_on,event_search_precision,integrator_type)

n_init=2


n_outputs=2


stepsize=0.3
horizon=2*stepsize
int_stepsize=stepsize/2



timeF=starttime
nextF=starttime

#------------------------------------------------------------------------------
#Jetson nano PWM

def pwmout():
    global timeV
    res=mega.readline()
    try:
        u=float(res[:-2].decode())
    except:
        res=mega.readline()
        u=float(res[:-2].decode())
    print("temp : ",u)
    
    timesave.append(timeV)
    tempsave.append(u)
    
    init_vars=fmipp.new_string_array(n_init)
    fmipp.string_array_setitem(init_vars,0,"time")
    fmipp.string_array_setitem(init_vars,1,"u")
    
    init_vals=fmipp.new_double_array(n_init)
    fmipp.double_array_setitem(init_vals,0,timeV)
    fmipp.double_array_setitem(init_vals,1,u)
    
    outputs=fmipp.new_string_array(n_outputs)
    fmipp.string_array_setitem(outputs,0,"time")
    fmipp.string_array_setitem(outputs,1,"y")
    
    fmippfmu.defineRealOutputs(outputs,n_outputs)
    
    status=fmippfmu.init("zigzag1",init_vars,init_vals,n_init,starttime,horizon,stepsize,int_stepsize)
    assert status==1
    
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(output_pin, 100)
    p.start(5)
    try:
        while True:
            start=time.time()
            #lst=testfunction(fmiversion,fmitype)
            result=fmippfmu.getRealOutputs()
            print(result)
            pwmvalue=10#round(result[0][1],0)
            print("pwmvalue : ",pwmvalue)
            print("volt : ", pwmvalue*0.0494)
            if pwmvalue > 100:
                pwmvalue=100
            elif pwmvalue < 0:
                pwmvalue=1
            p.ChangeDutyCycle(pwmvalue)
            end=time.time()
            print("time : ",end-start)
            timeV=round(timeV+(end-start),3)
    except KeyboardInterrupt:
        print("Ctrl+C")
        with open("input.csv","a",encoding="utf-8",newline="") as f:
            writer=csv.writer(f)
            i=0
            while len(timesave)!=i:
                writer.writerow([timesave[i],tempsave[i]])
                i=i+1
        
        with open("output.csv","a",encoding="utf-8") as o:
            writer=csv.writer(o)
            writer.writerows(result)
    finally:
        p.stop()
        GPIO.cleanup()

#------------------------------------------------------------------------------
#FMU simulation

def testfunction(fmi_version, fmi_type, solver="CVode", events=True, fmi_logging=False, show_plot=False):
    #if mega.readable():
    res=mega.readline()
    try:
        u=float(res[:-2].decode())
    except:
        res=mega.readline()
        u=float(res[:-2].decode())
    print("temp : ",u)
    
    input=np.array([(timeV,u)],dt)
    timesave.append(timeV)
    tempsave.append(u)
    
    result=fm.simulate_fmu(filename=fmu, validate=False, start_time=starttime, stop_time=stoptime, solver=solver, step_size=0.2, output_interval=0.2, record_events=events, start_values={outval:0.2}, input=input, fmi_call_logger=lambda s : print("[FMI]"+s) if fmi_logging else None)
    #"""if show_plot:
    #    plot_result(result=result, window_title=fmu+" Output", events=events, filename="./result.png")"""

    return result

#------------------------------------------------------------------------------
#main

if __name__=="__main__":
    pwmout()