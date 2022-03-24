import matplotlib.pyplot as plt
from matplotlib import animation
from serial import Serial
import matplotlib as mpl

t=0

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

#mpl.use("GTK3Agg")
mpl.rcParams['path.simplify']=True
mpl.rcParams['path.simplify_threshold']=1.0

fig,ax=plt.subplots()
line1,=ax.plot([],[],lw=2,color="g")
line2,=ax.plot([],[],lw=2,color="b")
ax.set_xlim(0,600)
ax.set_ylim(0,240)
line=[line1,line2]

def data_gen():
    t=data_gen.t
    while True:
        t=t+1
        Temp1,Temp2=Ardread()
        yield t, Temp1, Temp2

data_gen.t=0

xdata,t1data,t2data=[],[],[]

def run(data):
    t,Temp1,Temp2=data
    xdata.append(t)
    t1data.append(Temp1)
    t2data.append(Temp2)
    
    xmin,xmax=ax.get_xlim()
    if t>xmax:
        ax.set_xlim(xmin+1,xmax+1)
    
    line[0].set_data(xdata,t1data)
    line[1].set_data(xdata,t2data)
    return line

ani=animation.FuncAnimation(fig,run,data_gen,interval=10,blit=True,repeat=False)
plt.show()