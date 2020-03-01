import socket
import sys
import threading
import time
import read_settings as rs
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QStackedWidget, QTextBrowser, QTextEdit
from PyQt5 import QtCore
from PyQt5 import QtGui

app_version = "0.0.1"

def print_thread (name, delay):
    count = 0
    while count < 10:
        time.sleep(delay)
        count += 1
        print (name+": "+time.ctime(time.time()))


class Client(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.messageToSend=""

    def run(self):
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((rs.settings["ip"], int(rs.settings["port"])))
        except:
            print("Couldn't join server: "+rs.settings["ip"]+":"+rs.settings["port"])

        while(True):
            if(self.messageToSend!=""):
                byt = str.encode(self.messageToSend)
                client.send(byt)
                self.messageToSend=""


class MessageTaker(QtCore.QThread):
    def __init__(self, clientsock):
        QtCore.QThread.__init__(self)
        self.client = clientsock
    
    def run(self):
        while True:
            data = self.client.recv(4096)
            if not data: break
            from_client = data.decode()
            #print (from_client)
        print ("DC")


class Server(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)


    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messageTakers = list()

        print("Creating server on: "+rs.settings["ip"]+":"+rs.settings["port"])
        try:
            self.server.bind((rs.settings["ip"], int(rs.settings["port"])))
            self.server.listen(5)
        except:
            print("Error: failed to create server. IP or port is invalid.")
        
        print("Server created!")

        while(True):
            clientsock, address = self.server.accept()
            print(address[0]+" connected!")
            #this goes to new thread
            #self.messageTakers.append(MessageTaker(self.server, clientsock))
            #self.messageTakers[-1].start()
            #MessageTaker(self.server, clientsock).start()
            

class ChatWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.client = Client()
        

        self.msgBox = QTextBrowser(self)
        self.msgBox.setGeometry(0, 0, 400, 350)
        self.sendBox = QTextEdit(self)
        self.sendBox.setGeometry(0,350,350,50)
        sendButton = QPushButton("Send", self)
        sendButton.mouseReleaseEvent = self.SendMsg
        sendButton.setGeometry(350,350,50,50)

        parent.addWidget(self)


    def JoinServer(self):
        self.client.start()

    def SendMsg(self, event):
        messageText = self.sendBox.toPlainText()
        self.sendBox.setText("")
        self.client.messageToSend=messageText


class MainWindow(QStackedWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.server = Server()
        

        self.setFixedSize(400, 400)
        self.setWindowTitle("OpenMSG "+app_version)
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.initGUI()
        self.show()

    
    def initGUI(self):
        self.introWidget = QWidget()
        b1 = QPushButton("Join server", self.introWidget)
        b1.setGeometry(0, 250, 400, 50)
        b2 = QPushButton("Run server", self.introWidget)
        b2.setGeometry(0, 300, 400, 50)
        b3 = QPushButton("Exit", self.introWidget)
        b3.setGeometry(0, 350, 400, 50)

        b1.mouseReleaseEvent = self.JoinServer
        b2.mouseReleaseEvent = self.HostAndJoinServer
        b3.mouseReleaseEvent = self.ExitApp

        self.chatWidget = ChatWidget(self)
        
        self.addWidget(self.introWidget)
        self.addWidget(self.chatWidget)

        #b1.show()
        #b2.show()
        #b3.show()

    def showChatGUI(self):
        self.setCurrentIndex(1)
        self.chatWidget.JoinServer()

    def setMotive(self, stylesheet):
        self.styleSheet = stylesheet
        self.setStyleSheet(self.styleSheet)

    def ExitApp(self, event):
        #save current setings etc. before closing
        sys.exit()
    
    def JoinServer(self, event):
        self.showChatGUI()
        
    
    def HostAndJoinServer(self, event):
        self.server.start()
        self.showChatGUI()
        



if __name__=='__main__':
    rs.load_settings(r"server.txt")
    rs.load_stylesheet(r"stylesheet.txt")
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.setMotive(rs.stylesheet)
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

