import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication
import paho.mqtt.client as mqtt

from mqttutils import MqttClient
from ui.ui_main_window import Ui_MainWindow


# from src.mqttutils import *


class MainWindow(QMainWindow, Ui_MainWindow):
    # class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        self.setupUi(self)

        # mqtt client init
        self.is_connected = False
        self.mqtt_client = MqttClient()


    @pyqtSlot(bool)
    def on_pushButtonConnect_clicked(self, para):
        print("connecting to mqtt host: {}".format(self.lineEditHost.text()))
        host = self.lineEditHost.text()
        port = int(self.lineEditPort.text())
        self.mqtt_client.loop_start()
        self.mqtt_client.connect(host=host, port=port, keepalive=60)  # loop_start 先调用则阻塞， 后调用则不阻塞
        print("is_connected", self.mqtt_client.is_connected)

    @pyqtSlot()
    def on_pushButtonSub_clicked(self):
        print("sub to mqtt topic: {}".format(self.lineEditTopicSub.text()))
        topic = self.lineEditTopicSub.text()
        self.mqtt_client.subscribe(topic=topic, qos=1)

    @pyqtSlot()
    def on_pushButtonPub_clicked(self):
        print("pub to mqtt topic: {}".format(self.lineEditTopicPub.text()))
        topic = self.lineEditTopicPub.text()
        msg = self.lineEditMsgPub.text()
        self.mqtt_client.publish(topic=topic, payload=msg.encode())

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = MainWindow()
    mw.show()
    app.exec()
