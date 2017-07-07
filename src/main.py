import random
import sys
import uuid
from time import sleep

import datetime
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication
import paho.mqtt.client as mqtt

from mqttutils import MqttClient
from ui.ui_main_window import Ui_MainWindow


# from src.mqttutils import *


DEFAULT_HOST = "broker.mqttdashboard.com"

class MainWindow(QMainWindow, Ui_MainWindow):
    # class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        self.setupUi(self)

        self.checkBoxCleanSession.setChecked(True)
        self.spinBoxKeepAlive.setValue(60)
        self.pushButtonSub.setEnabled(False)
        self.pushButtonPub.setEnabled(False)

        self.lineEditHost.setText(DEFAULT_HOST)


        # mqtt client init
        self.is_connected = False
        self.mqtt_client = None

    def on_mqtt_msg(self, client, userdata, message:mqtt.MQTTMessage):
        msg = message.payload.decode()
        msg = str(datetime.datetime.now())[:-7] + ": " + message.topic + " == " + msg
        print(msg)
        self.textBrowserReceived.append(msg)

    def on_mqtt_connect(self, client, userdata, flags, rc):
        self.pushButtonSub.setEnabled(True)
        self.pushButtonPub.setEnabled(True)

    def on_mqtt_disconnect(self, client, userdata, flags, rc):
        self.pushButtonSub.setEnabled(False)
        self.pushButtonPub.setEnabled(False)


    @pyqtSlot()
    def on_pushButtonClientIdGenerate_clicked(self):
        client_id = uuid.uuid4()
        self.lineEditPortClientId.setText("qt_" + client_id.hex)

    @pyqtSlot(bool)
    def on_pushButtonConnect_clicked(self, para):
        host = self.lineEditHost.text()
        port = int(self.lineEditPort.text())
        print("connecting to mqtt host: {0}:{1}".format(host, port))

        client_id = self.lineEditPortClientId.text()
        keepalive = int(self.spinBoxKeepAlive.value())
        clean_session = self.checkBoxCleanSession.isChecked()
        auto_connect = self.checkBoxAutoConnect.isChecked()
        username = self.lineEditPortUserName.text()
        password = self.lineEditPortPassword.text()
        #
        # if self.mqtt_client.is_called_connect:
        #     # self.mqtt_client.loop_stop()
        #     self.mqtt_client.disconnect()

        # self.mqtt_client = MqttClient(client_id=client_id,
        #                               clean_session=clean_session,
        #                               )
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.reinitialise(client_id=client_id, clean_session=clean_session)
        else:
            self.mqtt_client = MqttClient(client_id=client_id, clean_session=clean_session)
            self.mqtt_client.on_message_handles.append(self.on_mqtt_msg)
            self.mqtt_client.on_connect_handles.append(self.on_mqtt_connect)
            self.mqtt_client.on_disconnect_handles.append(self.on_mqtt_disconnect)

        # self.mqtt_client.tls_set("d:/tmp/cert")

        try:
            self.mqtt_client.username_pw_set(username=username, password=password)
            self.mqtt_client.connect(host=host, port=port, keepalive=keepalive)  # loop_start 先调用则阻塞， 后调用则不阻塞
            # self.mqtt_client.connect(host=host, port=8883, keepalive=keepalive)  # loop_start 先调用则阻塞， 后调用则不阻塞
            self.mqtt_client.loop_start()
        # print("is_connected", self.mqtt_client.is_connected)
        except Exception as e:
            print(e)
    @pyqtSlot()
    def on_pushButtonSub_clicked(self):
        if self.mqtt_client.is_connected:
            print("sub to mqtt topic: {}".format(self.lineEditTopicSub.text()))
            topic = self.lineEditTopicSub.text()
            self.mqtt_client.subscribe(topic=topic, qos=1)
        else:
            print("sub failed, client is not connected")

    @pyqtSlot()
    def on_pushButtonPub_clicked(self):
        if self.mqtt_client.is_connected:
            print("pub to mqtt topic: {}".format(self.lineEditTopicPub.text()))
            topic = self.lineEditTopicPub.text()
            msg = self.lineEditMsgPub.text()
            self.mqtt_client.publish(topic=topic, payload=msg.encode())
        else:
            print("pub failed, client is not connected")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = MainWindow()
    mw.show()
    app.exec()
