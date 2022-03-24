from __future__ import print_function
import csv
import numpy as np
import fmpy as fm
from fmpy.util import plot_result

print("Library open")

infolist=[]
repllist=[]
ndellist=[]
finallist=[]

with open("fmu_info.txt","r",encoding="utf-8") as t:
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
   
    with open("output.csv","w",encoding="utf-8") as o:
        #print(result)
        wr=csv.writer(o)
        wr.writerows(result)    
    
    return result

if __name__=="__main__":
    testfunction(fmiversion,fmitype)
    
