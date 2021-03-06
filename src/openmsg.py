import socket
import sys
import threading
import time
import read_settings as rs
import command_parser as cp
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QAbstractScrollArea, QStackedWidget, QTextBrowser, QTextEdit
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal

APP_VERSION = "0.0.6"
CPU_DELAY = 0.1 #while(true) loops would eat up a lot of CPU if there is no delay

#Hears and sends data through socket to the server
class Client(QtCore.QObject):

    hearSignal = pyqtSignal(str)
    speakSignal = pyqtSignal()

    def __init__(self,UIBox, ip, port):
        super(Client, self).__init__()
        self.messageToSend=""
        self.logScreen = UIBox
        self.connected=False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Joining: "+ip+":"+str(port))
        try:
            self.sock.connect((ip, port))
            self.connected=True
        except:
            print("Couldn't join server: "+ip+":"+str(port))
            return

        self.hearSignal.connect(self.AppendMessage)
        self.speakSignal.connect(self.ScrollDown)

        self.tspeak = threading.Thread(target=self.Speak)
        self.thear = threading.Thread(target=self.Hear)

        self.tspeak.daemon = True
        self.thear.daemon = True

        self.tspeak.start()
        self.thear.start() 

    def AppendMessage(self, text):
        self.logScreen.insertPlainText(text)

    def ScrollDown(self):
        self.logScreen.verticalScrollBar().setValue(self.logScreen.verticalScrollBar().maximum())

    def Speak(self):
        byt = str.encode("/join "+rs.settings["nickname"])
        try:
            self.sock.send(byt)
        except:
            print("No connection!")
            return

        while(True):
            time.sleep(CPU_DELAY)
            if(self.messageToSend!=""):
                byt = str.encode(self.messageToSend)
                try:
                    self.sock.send(byt)
                    self.messageToSend=""
                    self.speakSignal.emit()
                except:
                    print("No connection!")
                    break
    
    def Hear(self):

        #Open by file or exe in 'utf-8' encoding so emojis can be used
        try:
            file = open(rs.current_file_dir+"\\server_log.txt",'a+', encoding='utf-8')
        except:
            file = open(rs.current_exe_dir+"\\server_log.txt",'a+', encoding='utf-8')

        #Keeps loading new messages
        while(True):
            time.sleep(CPU_DELAY)
            message = self.sock.recv(4096).decode()
            if(message!=""):
                message=message+"\n"
                file.write(message)
                self.hearSignal.emit(message)
                file.flush()    
        file.close()

#Simple class that manages connected clients
class Server():

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_list = [] #tuples of (socket, str nickname)
        print("Creating server on: "+rs.settings["ip"]+":"+rs.settings["port"])

        try:
            self.server.bind((rs.settings["ip"], int(rs.settings["port"])))
            self.server.listen(32)
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
            
            self.client_list.append([clientsock,"Anonymous"]) 
            t = threading.Thread(target=self.ClientThread,args=(self.client_list[-1],))
            t.daemon = True
            t.start()

    def RemoveClient(self, c):
        if c in self.client_list:
            self.client_list.remove(c)
            self.Broadcast(c[1]+" has left the room.")

    def ClientThread(self, client):
        while(True):
            time.sleep(CPU_DELAY)
            try:
                data = client[0].recv(4096)
            except:
                data = None

            if not data: 
                self.RemoveClient(client)
                break

            from_client = data.decode()

            #check whether it is a command or message
            if(from_client[0]=='/'):
                self.ParseCommand(from_client[1:], client)
            else:
                message = (client[1]+"("+str(client[0].getsockname()[0])+"): "+from_client)
                self.Broadcast(message)

    def Broadcast(self, message):
        for client in self.client_list:
            try:
                client[0].send(message.encode())
            except:
                self.RemoveClient(client)
                client[0].close()


    def ServerPrivateMessage(self, message, who):
        try:
            who[0].send(("(Server):").encode()+message.encode())
        except:
            self.RemoveClient(who)
            who[0].close()    

    def ParseCommand(self, command, who):
        task = command.split(' ')
        cp.Parse(task[0],who,task[1:],self)
                

                 
class ChatWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.msgBox = QTextBrowser(self)
        self.msgBox.setGeometry(0, 0, 400, 350)
        
        self.sendBox = QTextEdit(self)
        self.sendBox.setGeometry(0,350,350,50)
        self.sendBox.installEventFilter(self)
        sendButton = QPushButton("Send", self)
        sendButton.mouseReleaseEvent = self.SendMsg
        sendButton.setGeometry(350,350,50,50)

        parent.addWidget(self)

    def DisplayLogs(self, text):
        self.msgBox.setText(text)

    def JoinServer(self, ip, port):
        self.client = Client(self.msgBox, ip, port)
        if(self.client.connected==True):
            return True
        else:
            return False
        

    def SendMsg(self, event):
        messageText = self.sendBox.toPlainText()
        self.sendBox.setText("")
        self.client.messageToSend=messageText

    def eventFilter(self, obj, event):
        if(event.type() == QtCore.QEvent.KeyPress and obj is self.sendBox):
            if(event.key() == QtCore.Qt.Key_Return and self.sendBox.hasFocus()):
                self.SendMsg(None)
            else:
                return super().eventFilter(obj, event)
        return True
        


class MainWindow(QStackedWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(400, 400)
        self.setWindowTitle("OpenMSG "+APP_VERSION)
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

        self.ipline = QLineEdit(self.introWidget)
        self.portline = QLineEdit(self.introWidget)
        self.ipline.setGeometry(60,144,200,24)
        self.portline.setGeometry(270,144,70,24)

        iplabel = QLabel("Server IP", self.introWidget)
        portlabel = QLabel("Port", self.introWidget)
        iplabel.setGeometry(60,124,100,24)
        portlabel.setGeometry(270,124,100,24)

        self.ipline.setText(rs.settings["ip"])
        self.portline.setText(rs.settings["port"])

        self.nickline = QLineEdit(self.introWidget)
        self.nickline.setText(rs.settings["nickname"])
        self.nickline.setMaxLength(20)
        self.nickline.setGeometry(60,100,200,24)
        nicklabel = QLabel("Nickname", self.introWidget)
        nicklabel.setGeometry(60,80,200,24)

        #connect all QLineEdits to an event
        self.ipline.textEdited.connect(self.Reload)
        self.portline.textEdited.connect(self.Reload)
        self.nickline.textEdited.connect(self.Reload)

        b1.mouseReleaseEvent = self.JoinServer
        b2.mouseReleaseEvent = self.Host
        b3.mouseReleaseEvent = self.ExitApp

        self.chatWidget = ChatWidget(self)
        
        self.addWidget(self.introWidget)
        self.addWidget(self.chatWidget)

        #Reload is nescessary to reset wrong data from settings.txt
        self.Reload(None)

    def Reload(self,text):
        rs.settings["ip"]=self.ipline.text()
        rs.settings["port"]=self.portline.text()
        rs.settings["nickname"]=self.nickline.text()
        rs.reload_settings(r"settings.txt")

    def showChatGUI(self):
        self.setCurrentIndex(1)

    def setMotive(self, stylesheet):
        self.styleSheet = stylesheet
        self.setStyleSheet(self.styleSheet)

    def ExitApp(self, event):
        #save current setings etc. before closing
        sys.exit()
    
    def JoinServer(self, event):
        if(self.chatWidget.JoinServer(str(self.ipline.text()), int(self.portline.text()))):
            self.showChatGUI()
            rs.save_settings("settings.txt")
        
    def Host(self, event):
        rs.reload_settings("settings.txt")
        
        self.server = Server()
        if(self.chatWidget.JoinServer(str(self.ipline.text()), int(self.portline.text()))):
            self.showChatGUI()
            
    

if __name__=='__main__':
    rs.load_settings(r"settings.txt")
    rs.load_stylesheet(r"stylesheet.txt")
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.setMotive(rs.stylesheet)
    sys.exit(app.exec_())

