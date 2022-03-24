from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import random
import time
#
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter

fig = plt.figure()     #figure(도표) 생성



ax = plt.subplot(211, xlim=(0, 50), ylim=(0, 1024))
ax_2 = plt.subplot(212, xlim=(0, 50), ylim=(0, 512))


max_points = 50
max_points_2 = 50


line, = ax.plot(np.arange(max_points), 
                np.ones(max_points, dtype=np.float)*np.nan, lw=1, c='blue',ms=1)
line_2, = ax_2.plot(np.arange(max_points_2), 
                np.ones(max_points, dtype=np.float)*np.nan, lw=1,ms=1)


def init():
    return line
def init_2():
    return line_2


def animate(i):
    y = random.randint(0,1024)
    old_y = line.get_ydata()
    new_y = np.r_[old_y[1:], y]
    line.set_ydata(new_y)
    #print(new_y)
    return line

def animate_2(i):
    y_2 = random.randint(0,512)
    old_y_2 = line_2.get_ydata()
    new_y_2 = np.r_[old_y_2[1:], y_2]
    line_2.set_ydata(new_y_2)
    #print(new_y_2)
    return line_2

#------------------------------------------------------------------------------
def start_heat():
       consolelabel.config(text="Code Start")
       statusframe.config(bg="green")
       statuslabel.config(text="start", bg="green")
       pass

def stop_heat():
       consolelabel.config(text="Code Stop")
       statusframe.config(bg="red")
       statuslabel.config(text="stop", bg="red")
       pass

window = tkinter.Tk() #추가
window.title("Sealing Test")
window.geometry("1024x720+100+100")
window.resizable(False,False)

graphframe=tkinter.Frame(window, relief="solid", bd=2)
graphframe.pack(side="right", fill="both", expand=True)

canvas=FigureCanvasTkAgg(fig, master=graphframe) #
canvas.get_tk_widget().pack(fill="both", expand=True)

consoleframe=tkinter.Frame(graphframe, relief="solid", bd=2, bg="white")
consoleframe.pack(side="bottom", fill="both", expand=False)

fileframe=tkinter.Frame(consoleframe, relief="solid", bd=2)
fileframe.pack(side="top", fill="both", expand=False)

def findfile():
       fileframe.filename=tkinter.filedialog.askopenfilename(initialdir="/hone/pi/Downloads", title="Choose Your File", filetypes=(("fmu file", "*.fmu"),))
       filelabel_2.config(text=fileframe.filename)

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

statusframe=tkinter.Frame(actframe, relief="solid", bg="red")
statusframe.pack(side="bottom", fill="both", expand=True)

statuslabel=tkinter.Label(statusframe,text="stop", bg="red")
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

def topselect(self):
       value=topscale.get()
    
toplabel1=tkinter.Label(topframe, text="Heating Plate Top")
toplabel1.pack()       

topvar=tkinter.DoubleVar()

topscale=tkinter.Scale(topframe, variable=topvar, relief="sunken", command=topselect, orient="horizontal", showvalue=True, resolution=0.01, digit=3, to=5, length=200)
topscale.pack()

toplabel2=tkinter.Label(topframe, text="Min")
toplabel2.pack(anchor="w") 

topspinbox1=tkinter.Spinbox(topframe, from_=1, to=5, validate="all", values=1)
topspinbox1.pack()

toplabel3=tkinter.Label(topframe, text="Max")
toplabel3.pack(anchor="w") 

topspinbox2=tkinter.Spinbox(topframe, from_=1, to=5, validate="all", values=5)
topspinbox2.pack()

toplabel4=tkinter.Label(topframe, text="High Duration")
toplabel4.pack(anchor="w") 

topspinbox3=tkinter.Spinbox(topframe, validate="all")
topspinbox3.pack()

toplabel5=tkinter.Label(topframe, text="Low Duration")
toplabel5.pack(anchor="w") 

topspinbox4=tkinter.Spinbox(topframe, validate="all")
topspinbox4.pack()


bottomframe=tkinter.Frame(controlframe, relief="solid", bd=2)
bottomframe.pack(side="top",fill="both",expand=True)

def bottomselect(self):
       value=bottomscale.get()

label5_1=tkinter.Label(bottomframe, text="Heating Plate Bottom")
label5_1.pack()

bottomvar=tkinter.DoubleVar()

bottomscale=tkinter.Scale(bottomframe, variable=bottomvar, relief="sunken", command=bottomselect, orient="horizontal", showvalue=True, resolution=0.01, digit=3, to=5, length=200)
bottomscale.pack()

bottomlabel2=tkinter.Label(bottomframe, text="Min")
bottomlabel2.pack(anchor="w")

bottomspinbox1=tkinter.Spinbox(bottomframe, from_=1, to=5, validate="all", values=1)
bottomspinbox1.pack()

bottomlabel3=tkinter.Label(bottomframe, text="Max")
bottomlabel3.pack(anchor="w")

bottomspinbox2=tkinter.Spinbox(bottomframe, from_=1, to=5, validate="all", values=5)
bottomspinbox2.pack()

bottomlabel4=tkinter.Label(bottomframe, text="High Duration")
bottomlabel4.pack(anchor="w")

bottomspinbox3=tkinter.Spinbox(bottomframe, validate="all")
bottomspinbox3.pack()

bottomlabel5=tkinter.Label(bottomframe, text="Low Duration")
bottomlabel5.pack(anchor="w")

bottomspinbox4=tkinter.Spinbox(bottomframe, validate="all")
bottomspinbox4.pack()

#------------------------------------------------------------------------------

anim = animation.FuncAnimation(fig, animate  , init_func= init ,frames=200, interval=1, blit=False)
anim_2 = animation.FuncAnimation(fig, animate_2  , init_func= init_2 ,frames=200, interval=1, blit=False)
window.mainloop()
