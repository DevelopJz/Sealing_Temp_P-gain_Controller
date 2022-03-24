import csv
import serial
import time

mega=serial.Serial(port="/dev/ttyACM0",baudrate=9600,)

timeValue=0
timedelay=0.2

print("making csv file(Ctrl+C)")

with open("input.csv","wt",encoding="utf-8",newline="") as f:
    writer=csv.writer(f)
    writer.writerow(["time","u"])
    while True:
        if mega.readable():
            res=mega.readline()
        temp=float(res.decode())
        print(temp)
        timeValue=round(timeValue+timedelay,1)
        writer.writerow([timeValue,temp])
        time.sleep(timedelay)