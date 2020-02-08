from PyQt5 import QtCore, QtGui, QtWidgets
from main import Ui_MainWindow
import sys
import socket
import pickle
import random
import pyautogui
from threading import Thread
from pynput.mouse import Controller, Button

class Tracer(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.sock = None
        self.conn = None
        self.setWindowTitle('server side')
        self.installEventFilter(self)

        conn_thread = Thread(target=self.connect, daemon=True)
        conn_thread.start()

        ## new config for the video streaming
        self.pixmap = QtGui.QPixmap()
        self.label = QtWidgets.QLabel(self)
        self.label.resize(self.width(), self.height())
        self.setGeometry(QtCore.QRect(pyautogui.size()[0] // 4, pyautogui.size()[1] // 4, 800, 450))
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle("[SERVER] Remote Desktop: " + str(random.randint(99999, 999999)))
        self.start = Thread(target=self.ChangeImage, daemon=True)
        self.start.start()

    def ChangeImage(self):
        print('waiting for connection for video streaming')
        img_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        img_sock.bind(('', 9091))
        img_sock.listen(10)
        conn, addr = img_sock.accept()
        print('connected for the video')

        try:
            print("[SERVER]: CONNECTED: {0}!".format(addr[0]))
            while True:
                img_bytes = conn.recv(9999999)
                self.pixmap.loadFromData(img_bytes)
                self.label.setScaledContents(True)
                self.label.resize(self.width(), self.height())
                self.label.setPixmap(self.pixmap)
        except ConnectionResetError:
            QtWidgets.QMessageBox.about(self, "ERROR", "[SERVER]: The remote host forcibly terminated the existing connection!")
            conn.close()

    # here we need to send the ratio
    ## the equation for the ratio is 
    # x_ratio_pos = x/width
    # y_ratio_pos = y/height
    ## then when extracting the values at the server end
    # x = x_ratio_pos*width
    # y = y_ratio_pos*height
    # the format should be like one of the following 
    # ("L","P","x","y") => left pressed
    # ("L","R","x","y") => left released
    # ("R","P","x","y") => right pressed
    # ("R","R","x","y") => right realesed
    # ("0", "0", "x", "y") => no button pressed but cursor is moved
    def mouseMoveEvent(self, event):
        
        if self.conn:
            if self.positive(event.x()) and self.positive(event.y()):
                x = round(event.x()/self.width(), 2)
                y = round(event.y()/self.height(), 2)
                
                self.conn.send(pickle.dumps((0,0,x,y)))
                if event.button() == QtCore.Qt.NoButton:
                    print('nobutton : ', x,y)
                elif event.button() == QtCore.Qt.LeftButton:
                    print('left button : {}'.format((x,y)))
                elif event.button() == QtCore.Qt.RightButton:
                    print('right button : {}'.format((x,y)))
                else:
                    pass


    def mousePressEvent(self, event):
        if self.conn:
            if self.positive(event.x()) and self.positive(event.y()):
                x = round(event.x()/self.width(), 2)
                y = round(event.y()/self.height(), 2)
                if event.button() == QtCore.Qt.LeftButton:
                    print('left button pressed')
                    print(event.pos())
                    self.conn.send(pickle.dumps(("L","P", x, y)))
                elif event.button() == QtCore.Qt.RightButton:
                    print('right button pressed')
                    print(event.pos())
                    self.conn.send(pickle.dumps(("R","P", x, y)))

    def mouseReleaseEvent(self, event):
        if self.conn:
            if self.positive(event.x()) and self.positive(event.y()):
                x = round(event.x()/self.width(), 2)
                y = round(event.y()/self.height(), 2)
                if event.button() == QtCore.Qt.LeftButton:
                    print('leftf button Realeased')
                    print(event.pos())
                    self.conn.send(pickle.dumps(("L", "R", x, y)))
                elif event.button() == QtCore.Qt.RightButton:
                    print('right button Realeased')
                    print(event.pos())
                    self.conn.send(pickle.dumps(("R", "R", x, y)))


    def positive(self, number):
        if number > 0:
            return True
        else:
            return False

    def eventFilter(self, parent, e):
        if parent == self:
            if ( e.type() == 129): 
                return True
            else:
                return False
        else:
            return False
        # print(e.type())
        # return False

        
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', 9999))
        self.sock.listen(10)
        print('waying for connection ')
        self.conn, addr = self.sock.accept()
        print('connected')




if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    tracer = Tracer()
    tracer.show()
    if not app.exec_():
        tracer.conn.close()
        tracer.sock.close()


    