import sys
import fmpy as fm

fmu="/home/pi/Downloads/Downloads/FMU_File/FMUFile/FMU_TEST.fmu"

f=open("fmu_info.txt","w",encoding="utf-8")
stdout=sys.stdout
sys.stdout=f
fm.dump(fmu)
f.close()
sys.stdout=stdout
