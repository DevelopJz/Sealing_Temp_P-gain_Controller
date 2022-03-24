from multiprocessing import Process

def loop_a():
    while True:
        print("a")

def loop_b():
    while True:
        print("b")

if __name__=="__main__":
    Process(target=loop_a).start()
    Process(target=loop_b).start()