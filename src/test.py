import threading

def funA():
    i = 0
    while i<100:
        print(i)
        i=i+1
        if(i%10==0):
            t = threading.Thread(target=funB,args=(i,i/10))
            t.start()

def funB(j, level):
    while(j<100):
        print(":",level," : ",j)
        j = j + 10


tt = threading.Thread(target=funA)
tt.start()
        