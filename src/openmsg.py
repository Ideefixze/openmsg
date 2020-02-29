import socket
import sys
import threading
import time
import read_settings as rs
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit
from PyQt5 import QtCore
from PyQt5 import QtGui
def print_thread (name, delay):
    count = 0
    while count < 10:
        time.sleep(delay)
        count += 1
        print (name+": "+time.ctime(time.time()))


class MainWindow(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 400)
        self.setWindowTitle("OpenMSG")
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        #TODO: add dynamic loading of stylesheet
        self.styleSheet = '''

        MainWindow{
            background-color:#3a3a3a;
        }

        QPushButton{
            background-color:#4e4e4e;
            color: #ffffff;
            font-size: 18px;
        }
        '''

        self.initIntroGUI()
        self.setStyleSheet(self.styleSheet)
        self.show()
        

    def initIntroGUI(self):
        b1 = QPushButton("Join server", self)
        b1.setGeometry(0, 250, 400, 50)
        b1.setFont
        b2 = QPushButton("Run server", self)
        b2.setGeometry(0, 300, 400, 50)
        b3 = QPushButton("Exit", self)
        b3.setGeometry(0, 350, 400, 50)

        b3.mouseReleaseEvent = self.ExitApp

        b1.show()
        b2.show()
        b3.show()

    def ExitApp(self, event):
        #save current setings etc. before closing
        sys.exit()

if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

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

