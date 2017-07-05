from time import sleep

import paho.mqtt.client as mqtt
from threading import Thread


class MqttClient(mqtt.Client):
    def __init__(self, *args, **kwargs):
        super(MqttClient, self).__init__(*args, **kwargs)
        self.is_connected = False

        # The callback for when the client receives a CONNACK response from the server.
        def on_connect(client: mqtt.Client, userdata, flags, rc):
            print("Connected with result code " + str(rc))
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            # client.subscribe("$SYS/#")
            self.is_connected = True

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg: mqtt.MQTTMessage):
            print(msg.topic + " " + msg.payload.decode())

        def on_disconnect(client, userdata, self):
            print("disconnected!")
            self.is_connected = False

        self.on_connect = on_connect
        self.on_message = on_message
        self.on_disconnect = on_disconnect


