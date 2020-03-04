import os
import sys
current_file_path = __file__
current_file_dir = os.path.dirname(__file__)
current_exe_dir = os.path.dirname(sys.executable)

#dict that contains all loaded information from 
#load_settings in form of [key=val]
settings = dict()
stylesheet = str()

def load_settings(filename):

    #determining whether we are running from .py or .exe
    try:
        settings_file = open(current_exe_dir+"\\"+filename,'r')
    except:
        settings_file = open(current_file_dir+"\\"+filename,'r')

    while(settings_file.readable):
        line = settings_file.readline()
        line=line.replace('\n','')
        setting=line.split('=',1) 

        if(setting[0]==''):
            break

        settings[setting[0]] = setting[1]

    settings_file.close()

    print("Loaded settings from " + filename)
    
    #for i in settings:
        #print (i+" = "+settings[i])

def load_stylesheet(filename):
    try:
        ss_file = open(current_exe_dir+"\\"+filename,'r')
    except:
        ss_file = open(current_file_dir+"\\"+filename,'r')
    
    global stylesheet 
    stylesheet = ''.join(ss_file.readlines())
    print("Loaded stylesheet from "+filename)
    
    #print(stylesheet)
    


    
