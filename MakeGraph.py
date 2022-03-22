import matplotlib.pyplot as plt
import csv

t_axis1=[]
T1_axis1=[]
T2_axis1=[]

t_axis2=[]
T1_axis2=[]
T2_axis2=[]

t_axis3=[]
T1_axis3=[]
T2_axis3=[]

t_axis4=[]
T1_axis4=[]
T2_axis4=[]

t_axis5=[]
T1_axis5=[]
T2_axis5=[]

def csvfileread(filename,t,T1,T2,color1,color2,num):
    with open(filename,"r") as f:
        next(csv.reader(f))
        for row in csv.reader(f):
            t.append(float(row[0]))
            T1.append(float(row[1]))
            T2.append(float(row[2]))
    plt.plot(t,T1,color1,label="Temp"+num+"(Upper)")
    plt.plot(t,T2,color2,label="Temp"+num+"(Lower)")

csvfileread("input.csv",t_axis1,T1_axis1,T2_axis1,"b","g","1")

plt.title("Temp Graph")
plt.xlabel("Time (s)")
plt.ylabel("Temp ('C)")
plt.legend()

plt.savefig("Heater_PID_result.png")

plt.show()
