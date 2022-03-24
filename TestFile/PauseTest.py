import matplotlib.pyplot as plt
from serial import Serial
import matplotlib as mpl
import matplotlib.style as mplstyle
import time

t=0
T=[]
T1=[]
T2=[]


mega=Serial(port="/dev/ttyACM0",baudrate=9600,)

def Decode(A):
    A=A.decode()
    t1=float(A[1:7])
    t2=float(A[8:])
    return t1, t2
    
def Ardread():
    if mega.readable():
        res=mega.readline()
        code=Decode(res)
        return code
    else:
        print("Read Error (Ardread)")

mpl.use("GTK3Agg")
mpl.rcParams['path.simplify']=True
mpl.rcParams['path.simplify_threshold']=1.0
mpl.rcParams['agg.path.chunksize']=10000
mplstyle.use('fast')

plt.xlabel("Time (s)")
plt.ylabel("Temp ('C)")
plt.title("Temp Graph")

while True:
    start=time.time()
    Temp1,Temp2=Ardread()
    T.append(t)
    T1.append(Temp1)
    T2.append(Temp2)
    if len(T)>300:
        T.pop(0)
        T1.pop(0)
        T2.pop(0)
        
    line1,=plt.plot(T,T1,color="g")
    line2,=plt.plot(T,T2,color="b")
    
    plt.legend(handles=(line1,line2),labels=("Upper","Lower"),loc="upper left")
    plt.pause(1e-100)
    end=time.time()
    tim=round(end-start,3)
    print("Time : ",tim)
    t=t+tim

plt.show()
