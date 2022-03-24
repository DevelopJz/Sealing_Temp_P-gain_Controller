#import time
from matplotlib import pyplot as plt
#import numpy as np
from serial import Serial
import matplotlib as mpl
import matplotlib.style as mplstyle

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

t=[]
T1=[]
T2=[]

#x=np.linspace(0,50.,num=100)
#X,Y=np.meshgrid(x,x)
fig=plt.figure()
#ax1=fig.add_subplot(2,1,1)
ax1=fig.add_subplot()

#img=ax1.imshow(X,vmin=-1,vmax=1,interpolation="None",cmap="RdBu")

line1,=ax1.plot([],lw=2,color="b")
line2,=ax1.plot([],lw=2,color="g")
#text=ax2.text(0.8,0.5, "")

ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Temp ('C)")
ax1.set_title("Temp Graph")

ax1.set_xlim([0,10])
ax1.set_ylim([0,250])
xmin,xmax=ax1.get_xlim()

fig.canvas.draw()

axbackground=fig.canvas.copy_from_bbox(ax1.bbox)
#ax2background=fig.canvas.copy_from_bbox(ax2.bbox)
    
#plt.show()

#t_start=time.time()
i=0
while True:
    Temp1,Temp2=Ardread()
    t.append(i)
    T1.append(Temp1)
    T2.append(Temp2)
    #img.set_data(np.sin(X/3.+k)*np.cos(Y/3.+k))
    line1.set_data(t,T1)
    line2.set_data(t,T2)
    #tx="Mean Frame Rate : \n {fps:.3f}FPS".format(fps=((i)/(time.time()-t_start)))
    #text.set_text(tx)
    
    if i>xmax:
        ax1.set_xlim(xmin+1,xmax+1)
        
    fig.canvas.restore_region(axbackground)
    #fig.canvas.restore_region(ax2background)
    
    #ax1.draw_artist(img)
    ax1.draw_artist(line1)
    ax1.draw_artist(line2)
    #ax2.draw_artist(text)
    
    #fig.canvas.blit(ax2.bbox)
    fig.canvas.blit(ax1.bbox)
        
    """else:
        fig.canvas.draw()"""
        
    fig.canvas.flush_events()
    i=i+1
#plt.show()