#Import tkinter package
import tkinter as tk
import time
#Define a window name
root1 = tk.Tk()
text_variable = tk.DoubleVar()
#declare the spinbox widget by assigning values to from_, to and increment
spin_box = tk.Spinbox(root1,from_=1.0,to=50.0,increment=1.0,textvariable=text_variable)
#To show the content in the window
spin_box.pack()
while True:
	print(spin_box.get())
	time.sleep(2)
	root1.update()
#root1.mainloop()
