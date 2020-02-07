
from main import Ui_MainWindow
import sys
from threading import Thread
import pickle
import socket
from pynput.mouse import Button, Controller
from win32api import GetSystemMetrics

class Tracer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('10.14.30.203', 9999))
        print('connected successfully')
        self.x = 0
        self.y = 0
        self.mouse = Controller()
        self.receiv()

    def receiv(self):
        while True:
            print('receiving')
            received = self.sock.recv(1024)
            button, status, x, y = pickle.loads(received)
            x = round(GetSystemMetrics(0) * x, 0)
            y = round(GetSystemMetrics(1) * y, 0)
            print(button, status, x, y)
            self.x = int(x)
            self.y = int(y)

            
            self.execute(button, status, self.x, self.y)

    def execute(self, btn, status, x, y):
        if btn == "R":
            btn = Button.right
        else:
            btn = Button.left


        if status == "P":
            self.mouse.position = (x, y)
            self.mouse.press(btn)
        elif status == "R":
            self.mouse.release(btn)
        else:
            self.mouse.position = (x, y)
        


if __name__ == "__main__":
    trace = Tracer()
    