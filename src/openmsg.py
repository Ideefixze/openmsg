import socket
import sys
import threading
import time
import read_settings as rs
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QAbstractScrollArea, QStackedWidget, QTextBrowser, QTextEdit
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal

app_version = "0.0.2"

#Hears and sends data through socket to the server
class Client:

    #hearSignal = pyqtSignal(str)

    def __init__(self, UIBox):
        self.messageToSend=""
        self.logScreen = UIBox

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Joining: "+rs.settings["ip"]+":"+rs.settings["port"])
        try:
            self.sock.connect((rs.settings["ip"], int(rs.settings["port"])))
        except:
            print("Couldn't join server: "+rs.settings["ip"]+":"+rs.settings["port"])
            return

        #self.hearSignal.connect(self.AppendMessage)

        #Load saved logs of this server
        try:
            file = open(rs.current_file_dir+"\\server_log.txt",'r+')
        except:
            file = open(rs.current_exe_dir+"\\server_log.txt",'r+')
        text = ''.join(file.readlines())

        self.logScreen.insertPlainText(text)
        self.logScreen.verticalScrollBar().setValue(self.logScreen.verticalScrollBar().maximum())
        file.close()

        tspeak = threading.Thread(target=self.Speak)
        thear = threading.Thread(target=self.Hear)

        tspeak.daemon = True
        thear.daemon = True

        tspeak.start()
        thear.start() 

    def Speak(self):
        while(True):
            if(self.messageToSend!=""):
                byt = str.encode(self.messageToSend)
                try:
                    self.sock.send(byt)
                    self.messageToSend=""
                except:
                    print("No connection!")
                    break

    
    def Hear(self):
        
        #self.hearSignal.emit(text)
        try:
            file = open(rs.current_file_dir+"\\server_log.txt",'a+')
        except:
            file = open(rs.current_exe_dir+"\\server_log.txt",'a+')

        #Keeps loading new messages
        while(True):
            message = self.sock.recv(4096).decode()
            if(message!=""):
                #print(message)
                message=message+"\n"
                file.write(message)
                self.logScreen.insertPlainText(message)
                #self.hearSignal.emit(text)    
        file.close()

#Simple class that manages connected clients
class Server():

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_list = []
        print("Creating server on: "+rs.settings["ip"]+":"+rs.settings["port"])

        try:
            self.server.bind((rs.settings["ip"], int(rs.settings["port"])))
            self.server.listen(10)
        except:
            print("Error: failed to create server. IP or port is invalid.")
            return

        print("Server created!")
        self.acceptthread = threading.Thread(target=self.AcceptClients)
        self.acceptthread.daemon = True
        self.acceptthread.start()
    
    def AcceptClients(self):
        while(True):

            print("(Server): Waiting for a new client...  currently there are: "+str(len(self.client_list))+" guests.")
            clientsock, address = self.server.accept()
            print("(Server): "+address[0]+" connected!")
            
            self.client_list.append(clientsock)
            self.Broadcast("(Server): Hello "+address[0]+"!")
            t = threading.Thread(target=self.ClientThread,args=(clientsock,))
            t.daemon = True
            t.start()

    def RemoveClient(self, c):
        if c in self.client_list:
            self.client_list.remove(c)

    def ClientThread(self, client):
        while(True):
            try:
                data = client.recv(4096)
            except:
                data = None

            if not data: 
                self.RemoveClient(client)
                break
            from_client = data.decode()
            message = (str(client.getsockname()[0])+": "+from_client)
            self.Broadcast(message)

    def Broadcast(self, message):
        for client in self.client_list:
            try:
                client.send(message.encode())
            except:
                client.close()
                self.RemoveClient(client)
                 

class ChatWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.msgBox = QTextBrowser(self)
        self.msgBox.setGeometry(0, 0, 400, 350)
        
        self.sendBox = QTextEdit(self)
        self.sendBox.setGeometry(0,350,350,50)
        sendButton = QPushButton("Send", self)
        sendButton.mouseReleaseEvent = self.SendMsg
        sendButton.setGeometry(350,350,50,50)

        parent.addWidget(self)

    def DisplayLogs(self, text):
        self.msgBox.setText(text)

    def JoinServer(self):
        self.client = Client(self.msgBox)
        

    def SendMsg(self, event):
        messageText = self.sendBox.toPlainText()
        self.sendBox.setText("")
        self.client.messageToSend=messageText


class MainWindow(QStackedWidget):

    def __init__(self, parent=None):
        super().__init__(parent)


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
        b2.mouseReleaseEvent = self.Host
        b3.mouseReleaseEvent = self.ExitApp

        self.chatWidget = ChatWidget(self)
        
        self.addWidget(self.introWidget)
        self.addWidget(self.chatWidget)

        #b1.show()
        #b2.show()
        #b3.show()

    def showChatGUI(self):
        self.setCurrentIndex(1)

    def setMotive(self, stylesheet):
        self.styleSheet = stylesheet
        self.setStyleSheet(self.styleSheet)

    def ExitApp(self, event):
        #save current setings etc. before closing
        sys.exit()
    
    def JoinServer(self, event):
        self.chatWidget.JoinServer()
        self.showChatGUI()
        
    def Host(self, event):
        self.server = Server()
    

if __name__=='__main__':
    rs.load_settings(r"server.txt")
    rs.load_stylesheet(r"stylesheet.txt")
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.setMotive(rs.stylesheet)
    sys.exit(app.exec_())

