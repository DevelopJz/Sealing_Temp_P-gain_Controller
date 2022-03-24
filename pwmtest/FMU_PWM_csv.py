from __future__ import print_function
import csv
import numpy as np
import fmpy as fm
from fmpy.util import plot_result
import RPi.GPIO as GPIO
import time

print("Library open")

output_pins = {
       'JETSON_XAVIER': 18,
       'JETSON_NANO': 33,
       'JETSON_NX': 33,
       'CLARA_AGX_XAVIER': 18,
}
output_pin = output_pins.get(GPIO.model, None)
if output_pin is None:
       raise Exception('PWM not supported on this board')


infolist=[]
repllist=[]
ndellist=[]
finallist=[]

with open("/home/pi/Downloads/Downloads/FMU_File/fmpytest/fmu_info.txt","r",encoding="utf-8") as t:
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
#print(ndellist)

delversion="FMIVersion"
deltype="FMIType"
delname="ModelName"
delstop="StopTime"
deltol="Tolerance"
delinput="uinput"
repoutput="output"

finallist.append(ndellist[0].replace(delversion,""))
finallist.append(ndellist[1].replace(deltype,""))
finallist.append(ndellist[2].replace(delname,""))
finallist.append(ndellist[3].replace(delstop,""))
finallist.append(ndellist[4].replace(deltol,""))
finallist.append(ndellist[5].replace(delinput,""))
finallist.append(ndellist[6].replace(repoutput,""))

#print(finallist)
fmiversion=finallist[0]
fmitype=finallist[1]
fmu="/home/pi/Downloads/Downloads/FMU_File/FMUFile/"+finallist[2]+".fmu"
stoptime=float(finallist[3])
tol=float(finallist[4])
starttime=float(finallist[5])
outval=finallist[6]

def pwmout():
       timelist=[]
       voltlist=[]
       templist=[]
       # Pin Setup:
       # Board pin-numbering scheme
       GPIO.setmode(GPIO.BOARD)
       # set pin as an output pin with optional initial state of HIGH
       GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
       p = GPIO.PWM(output_pin, 100)
       incr = 0
       with open("output.csv","r",encoding="utf-8") as h:
              lines=h.readline()
              while lines:
                     templist=list(lines.replace("\n","").split(","))
                     timelist.append(round(float(templist[0]),3))
                     voltlist.append(round(float(templist[1])/4*20.408,1))
                     lines=h.readline()
              #print("time : ",timelist)
              #print("volt : ",voltlist)

       p.start(1)
    
       #print("PWM running. Press CTRL+C to exit.")
       try:
              while incr!=len(voltlist):
                     p.ChangeDutyCycle(voltlist[incr])
                     print("val : ",voltlist[incr])
                     incr=incr+1
                     time.sleep(0.2)
                     #print("incr : ",incr)
       finally:
              p.stop()
              GPIO.cleanup()

def testfunction(fmi_version,
                 fmi_type,
                 solver="CVode",
                 events=True,
                 fmi_logging=False,
                 show_plot=True):
    
    input=np.genfromtxt("input.csv",delimiter=",",names=True)
    result=fm.simulate_fmu(
        filename=fmu,
        validate=False,
        start_time=starttime,
        stop_time=stoptime,
        solver=solver,
        step_size=1e-3,
        output_interval=0.002,
        record_events=events,
        start_values={outval:0.2},
        input=input,
        fmi_call_logger=lambda s : print("[FMI]"+s) if fmi_logging else None)
    
    if show_plot:
        plot_result(result=result,
                    window_title="FMU_TEST.fmu Output",
                    events=events,
                    filename="./result.png")
   
       
    with open("output.csv","w",encoding="utf-8") as o:         #w+a
        #print(result)
        wr=csv.writer(o)
        wr.writerows(result)    
    
    return result

if __name__=="__main__":
    result=testfunction(fmiversion,fmitype)
    #print(result)
    pwmout()
    
