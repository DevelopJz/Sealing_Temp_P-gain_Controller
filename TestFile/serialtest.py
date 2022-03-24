from serial import Serial

mega=Serial(port="/dev/ttyACM0",baudrate=9600,)

def Decode(A):
    A=A.decode()
    index=A.find("V")
    #print(index)
    t1=float(A[1:index])
    t2=float(A[index+1:])
    return t1, t2

def Ardread():
    if mega.readable():
        #mega.flushInput()
        res=mega.readline()
        code=Decode(res)
        return code
    else:
        print("Read Error (Ardread)")
        
Temp1,Temp2=Ardread()
print("Temp1 : ",Temp1)
print("Temp2 : ",Temp2)