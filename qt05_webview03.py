import sys
import time
import threading
import os
from multiprocessing import Process, Lock, Manager, Queue

from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *
import serial


root_path = os.path.abspath(os.path.dirname('__file__'))

################################################
#######创建主窗口
################################################
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('My Browser')  # 窗口标题
        self.setGeometry(5, 30, 1355, 730)  # 设置初始窗口位置坐标（左上，右下）

        self.showMaximized()  # 最大化
        self.setWindowFlags(Qt.FramelessWindowHint)  # 隐藏标题栏
        self.webview = WebEngineView()  # 浏览器初始化
        print(root_path)
        # 开启进入初始界面
        url = root_path + r"/mirror_system/Web_Project/index.html"
        url = url.replace('\\', '/')  # url
        print(url)

        self.webview.load(QUrl(url))
        self.setCentralWidget(self.webview)

        #self.ser1 = serial.Serial("COM8", 9600, timeout=0.5)
        #self.ser2 = serial.Serial("COM11", 9600, timeout=0.5)

        #self.ser1.write('\x11'.encode())
        #self.ser2.write('\x11'.encode())
        # ser1 = serial.Serial("COM5", 115200, timeout=0.5)
        # ser1 = serial.Serial("COM5", 115200, timeout=0.5)
        # ser1 = serial.Serial("COM5", 115200, timeout=0.5)


################################################
#######创建浏览器
################################################
class WebEngineView(QWebEngineView):
    windowList = []

    # 重写createwindow()
    def createWindow(self, QWebEnginePage_WebWindowType):
        new_webview = WebEngineView()
        new_window = MainWindow()
        new_window.setCentralWidget(new_webview)
        # new_window.show()
        self.windowList.append(new_window)  # 注：没有这句会崩溃！！！
        return new_webview


################################################
#######程序入门
################################################

class qt_main:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.w = MainWindow()

    def exec(self):
        self.w.show()
        self.app.exec_()

    def js_Callback(self, result):
        print(result)

    def changeSize(self, width):
        self.w.webview.page().runJavaScript(f'widthAdd({width});')

    def movePos(self, x, y):
        self.w.webview.page().runJavaScript(f'movePos({x}, {y});')

    def proRate(self, id_name, rate):
        self.w.webview.page().runJavaScript(f'pro_rate("{id_name}", {rate});')

    def location(self, page_name):
        self.w.webview.page().runJavaScript(f'window.location.href="{page_name}.html";')

    def proRateControlPage(self, rate):
        self.w.webview.page().runJavaScript(f'updateChooseConfirmRate({rate});')

    def chooseModulesControlPage(self, module_num):
        self.w.webview.page().runJavaScript(f'chooseModules({module_num});')

    def controlOpenModule(self, module_num):
        self.w.webview.page().runJavaScript(f'controlOpenModule({module_num});')
        if module_num < 3:
            self.w.ser1.write('\x01'.encode())
        else:
            self.w.ser2.write('\x01'.encode())


    def controlCloseModule(self, module_num):
        self.w.webview.page().runJavaScript(f'controlCloseModule({module_num});')
        if module_num < 3:
            self.w.ser1.write('\x11'.encode())
        else:
            self.w.ser2.write('\x11'.encode())


def changeValue(obj, lk, q):
    while True:
        with lk:
            info = q.get()
            if info['isChange']:
                # 大小
                if info['name'] == 'Size':
                    value = info['value']
                    obj.changeSize(value)
                # 位置偏移
                elif info['name'] == 'Pos':
                    x, y = value = info['value']
                    obj.movePos(x, y)
                # 充能进度
                elif info['name'] == 'next_back_rate':
                    id_name, rate = value = info['value']
                    print(id_name, rate)
                    obj.proRate(id_name, rate)
                # 控制页面的进度
                elif info['name'] == 'choose_rate_for_control':
                    value = info['value'][1]
                    obj.proRateControlPage(value)
                # 重定位
                elif info['name'] == 'location':
                    value = info['value']
                    obj.location(value)
                # 选择模块
                elif info['name'] == 'choose_modules_for_control':
                    value = info['value']
                    obj.chooseModulesControlPage(value)
                # 控制模块
                elif info['name'] == 'control_open_module':
                    print(info)
                    value = info['value']
                    obj.controlOpenModule(value)

                elif info['name'] == 'control_close_module':
                    value = info['value']
                    obj.controlCloseModule(value)



def runWindow(lk, q):
    Ball = qt_main()
    Ball.w.webview.page().runJavaScript('123;')
    t2 = threading.Thread(target=changeValue, args=(Ball, lk, q))
    t2.start()
    Ball.exec()


def main(lk, q):
    t1 = Process(target=runWindow, args=(lk, q))
    t1.start()
    t1.join()



if __name__ == '__main__':
    lock = Lock()
    m = Queue()
    main(lock, m)
    print(123145)
