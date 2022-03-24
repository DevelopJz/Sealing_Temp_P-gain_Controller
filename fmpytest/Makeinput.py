import csv
with open("input.csv","wt",encoding="utf-8",newline="") as f:
    writer=csv.writer(f)
    writer.writerow(["time","u"])
    i=0.0
    j=0
    while(i<5.2):
        writer.writerow([i,j])
        i=i+0.2
        i=round(i,1)
        j=j+1