import os
import random
import sys
import uuid
from PyQt5 import Qt
from time import sleep

import datetime
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication
import paho.mqtt.client as mqtt

from mqttutils import MqttClient
from ui.ui_main_window import Ui_MainWindow

import logging

LOG_PATH = "../log/"
LOG_FILENAME = "log.txt"

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH, exist_ok=True)

fileLogHandler = logging.FileHandler(os.path.join(LOG_PATH, LOG_FILENAME))
streamLogHandler = logging.StreamHandler()
logging.basicConfig(handlers=[fileLogHandler, streamLogHandler],
                    format="%(levelname)s: %(name)s: %(asctime)s ==> %(message)s",
                    datefmt="%y-%m-%d %H:%M:%S",
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_HOST = "broker.mqttdashboard.com"


class MainWindow(QMainWindow, Ui_MainWindow):
    # class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        self.setupUi(self)

        self.setWindowTitle("MQTT PyQt Client")
        self.checkBoxCleanSession.setChecked(True)
        self.spinBoxKeepAlive.setValue(60)
        self.pushButtonSub.setEnabled(False)
        self.pushButtonPub.setEnabled(False)
        self.pushButtonUnsub.setEnabled(False)

        self.lineEditHost.setText(DEFAULT_HOST)

        self.comboBoxQosSub.setItemData(0, 0)
        self.comboBoxQosSub.setItemData(1, 1)
        self.comboBoxQosSub.setItemData(2, 2)
        self.comboBoxQosPub.setItemData(0, 0)
        self.comboBoxQosPub.setItemData(1, 1)
        self.comboBoxQosPub.setItemData(2, 2)

        # combobox edit
        self.comboBoxSubTopics.setEditable(True)
        self.comboBoxSubTopics.setEditText("pyqttopic/#")

        self.statusbar.show()
        self.statusbar.showMessage("statusbar message here!", msecs=5000 )

        # mqtt client init
        self.is_connected = False
        self.mqtt_client = None




    # def on_comboBoxSubTopics_editTextChanged(self, s):
    #     logger.debug(self.comboBoxSubTopics.currentText())
    @pyqtSlot(int)
    def on_comboBoxSubTopics_currentIndexChanged(self, i):
        logger.debug("current index {}".format(i))

    def sub_unsubscribe(self, sub, topic, qos=0):
        if self.mqtt_client.is_connected:
            if sub:
                logger.info("sub to mqtt topic: {}".format(topic))
                self.mqtt_client.subscribe(topic=topic, qos=qos)
            else:
                logger.info("sub to mqtt topic: {}".format(topic))
                self.mqtt_client.unsubscribe(topic=topic)

        else:
            logger.info("sub failed, client is not connected")

    @pyqtSlot()
    def on_pushButtonUnsub_clicked(self):
        topic = self.comboBoxSubTopics.currentText()
        self.sub_unsubscribe(False, topic=topic)


    def on_mqtt_msg(self, client, userdata, message: mqtt.MQTTMessage):
        msg = message.payload.decode()
        logger.info("client received msg: topic:{0} ||  payload:{1}".format(message.topic, msg))
        msg = str(datetime.datetime.now())[:-7] + ": " + message.topic + " == " + msg
        self.textBrowserReceived.append(msg)

    def on_mqtt_connect(self, client, userdata, flags, rc):
        logger.info("client connected userdata:{0} || flags:{1} ||  rc:{2}".format(userdata, flags, rc))
        self.pushButtonSub.setEnabled(True)
        self.pushButtonPub.setEnabled(True)
        self.pushButtonUnsub.setEnabled(True)
        self.statusbar.showMessage("mqtt client connected success!", msecs=5000)

    def on_mqtt_disconnect(self, client, userdata, rc):
        logger.info("client connected userdata:{0} || rc:{1}".format(userdata, rc))
        self.pushButtonSub.setEnabled(False)
        self.pushButtonPub.setEnabled(False)
        self.pushButtonUnsub.setEnabled(False)

    # @pyqtSlot(int)
    # def on_comboBoxQosSub_currentIndexChanged(self, *args):
    #     logger.debug(args)

    @pyqtSlot()
    def on_pushButtonClientIdGenerate_clicked(self):
        client_id = uuid.uuid4()
        self.lineEditPortClientId.setText("qt_" + client_id.hex)

    @pyqtSlot(bool)
    def on_pushButtonConnect_clicked(self, para):
        host = self.lineEditHost.text()
        port = int(self.lineEditPort.text())
        logger.info("connecting to mqtt host: {0}:{1}".format(host, port))

        client_id = self.lineEditPortClientId.text()
        keepalive = int(self.spinBoxKeepAlive.value())
        clean_session = self.checkBoxCleanSession.isChecked()
        auto_connect = self.checkBoxAutoConnect.isChecked()
        username = self.lineEditPortUserName.text()
        password = self.lineEditPortPassword.text()

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
            rc = self.mqtt_client.connect(host=host, port=port, keepalive=keepalive)  # loop_start 先调用则阻塞， 后调用则不阻塞
            # self.mqtt_client.connect(host=host, port=8883, keepalive=keepalive)  # loop_start 先调用则阻塞， 后调用则不阻塞
            logger.info("client called connect with rc: {}".format(rc))
            self.statusbar.showMessage("mqtt client is connecting!", msecs=5000)
            self.mqtt_client.loop_start()

        except Exception as e:
            logger.info(e)

    @pyqtSlot()
    def on_pushButtonSub_clicked(self):
        if self.mqtt_client.is_connected:
            # logger.info("sub to mqtt topic: {}".format(self.lineEditTopicSub.text()))
            # topic = self.lineEditTopicSub.text()
            topic = self.comboBoxSubTopics.currentText()
            qos = self.comboBoxQosSub.currentData()
            self.sub_unsubscribe(True, topic=topic, qos=qos)
            # self.mqtt_client.subscribe(topic=topic, qos=qos)
        else:
            logger.info("sub failed, client is not connected")

    @pyqtSlot()
    def on_pushButtonPub_clicked(self):
        if self.mqtt_client.is_connected:
            logger.info("pub to mqtt topic: {}".format(self.lineEditTopicPub.text()))
            topic = self.lineEditTopicPub.text()
            msg = self.lineEditMsgPub.text()

            retained = self.checkBoxRetainedPub.isChecked()
            qos = self.comboBoxQosPub.currentData()

            if msg:
                self.mqtt_client.publish(topic=topic, payload=msg.encode(), qos=qos, retain=retained)
            else:
                self.mqtt_client.publish(topic=topic, payload=None, qos=qos, retain=retained)
        else:
            logger.info("pub failed, client is not connected")

    def on_(self):
        self.close

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = MainWindow()
    mw.show()
    app.exec()
