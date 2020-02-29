import socket
import sys
import threading
import time
import read_settings as rs

def print_thread (name, delay):
    count = 0
    while count < 10:
        time.sleep(delay)
        count += 1
        print (name+": "+time.ctime(time.time()))



rs.load_settings(r"server.txt");
print (rs.settings["greeting_msg"])

'''
try:
    print ("Starting threads...")
    t1 = threading.Thread(target=print_thread,args=("A", 0.1)) 
    t2 = threading.Thread(target=print_thread,args=("B", 0.15))
    t1.start();
    t2.start();
except:
    print ("Error: can't start threads")
    '''

