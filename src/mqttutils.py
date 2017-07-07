from time import sleep

import paho.mqtt.client as mqtt
from threading import Thread

from copy import deepcopy, copy


class MqttClient(mqtt.Client):

    def __init__(self, client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp"):
        super(MqttClient, self).__init__(client_id, clean_session, userdata, protocol, transport)
        self.is_connected = False

        self.on_message_handles = []
        self.on_connect_handles = []
        self.on_disconnect_handles = []

        # The callback for when the client receives a CONNACK response from the server.
        def on_connect(client: mqtt.Client, userdata, flags, rc):
            print("Connected with result code " + str(rc), flags)
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            # client.subscribe("$SYS/#")
            if rc == 0:
                self.is_connected = True

            for handle in self.on_connect_handles:
                if callable(handle):
                    handle(client, userdata, flags, rc)

        def on_disconnect(client, userdata, rc):
            self.is_connected = False
            print("Disconnect from broker with result code : " + str(rc))
            for handle in self.on_disconnect_handles:
                if callable(handle):
                    handle(client, userdata, rc)

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg: mqtt.MQTTMessage):
            print(msg.topic + " " + msg.payload.decode())
            for handle in self.on_message_handles:
                if callable(handle):
                    handle(client, userdata, msg)

        self.on_connect = on_connect
        self.on_message = on_message
        self.on_disconnect = on_disconnect


    def reinitialise(self, *args, **kwargs):
        try:

            copy_on_message_handles = copy(self.on_message_handles)
            copy_on_connect_handles = copy(self.on_connect_handles)
            copy_on_disconnect_handles = copy(self.on_disconnect_handles)
            super(MqttClient, self).reinitialise(*args, **kwargs)
            # mqtt.Client.reinitialise(self, *args, **kwargs)

            self.on_message_handles = copy_on_message_handles
            self.on_connect_handles = copy_on_connect_handles
            self.on_disconnect_handles = copy_on_disconnect_handles
        except Exception as e:
            print(e)

