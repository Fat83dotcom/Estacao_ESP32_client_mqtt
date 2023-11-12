import json
import paho.mqtt.client as mqtt
from time import strftime, localtime
from DataBaseManager.OperationalDataBase import Sensors, DataBasePostgreSQL
from DataBaseManager.settings import banco


class VerifySensors:
    def __init__(self) -> None:
        dbPostgreSQL = DataBasePostgreSQL(banco)
        self.sensorsInstace = Sensors(dbPostgreSQL)
        self.__sensorsOnDataBase: list[tuple] = [
            sens for sens in self.__searchSensors()
        ]

    @property
    def sensors(self):
        return self.__sensorsOnDataBase

    @sensors.setter
    def sensors(self, value):
        if isinstance(value, str):
            self.__sensorsOnDataBase.append(value)
        else:
            raise ValueError(
                f'Verifique a entrada mac dos sensores! -> {value}'
            )

    def searchSensors(self):
        pass


topic_sub = "ESP32_Sensors_BME280"


def on_message(client, userdata, msg):
    msgDecode = str(msg.payload.decode('utf-8', 'ignore'))
    msgJson = json.loads(msgDecode)
    print(msgJson)


mqttBroker = 'broker.hivemq.com'
port = 1883
client = mqtt.Client('Python_Fernando')
client.connect(mqttBroker, port)
while 1:
    client.subscribe(topic_sub)
    client.on_message = on_message
    client.loop_forever()
