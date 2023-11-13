import json
import paho.mqtt.client as mqtt
from time import strftime, localtime, time
from DataBaseManager.OperationalDataBase import Sensors, DataBasePostgreSQL
from DataBaseManager.OperationalDataBase import DataSensors
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
            if self.__insertSensors(value):
                self.__sensorsOnDataBase.append(value)
        else:
            raise ValueError(
                f'Verifique a entrada mac dos sensores! -> {value}'
            )

    def __searchSensors(self):
        result: list = self.sensorsInstace.execSelectOnTable(
            table='sensor',
            collCodiction='mac',
            condiction='',
            conditionLiteral='',
        )
        if result is None:
            return []
        else:
            return result

    def __insertSensors(self, *args) -> bool:
        if self.sensorsInstace.execInsertTable(
            *args,
            table='sensor',
            collumn=('mac',),
        ):
            return True
        else:
            return False

    def getSensorMac(self) -> list:
        if self.__sensorsOnDataBase:
            sensorMacs: list = [macs[2] for macs in self.__sensorsOnDataBase]
            return sensorMacs
        else:
            return []


topic_sub = "ESP32_Sensors_BME280"

sens = VerifySensors()

receiveDataOnSensors: dict = {}


def on_message(client, userdata, msg):
    msgDecode = str(msg.payload.decode('utf-8', 'ignore'))
    receiveDataOnSensors: dict = json.loads(msgDecode)
    receiveDataOnSensors['dataHora'] = strftime(
        '%d/%m/%Y %H:%M:%S', localtime(int(receiveDataOnSensors['dataHora']))
    )
    if receiveDataOnSensors['IDMac'] not in sens.getSensorMac():
        sens.sensors = receiveDataOnSensors['IDMac']
    else:
        print('já tem!')
    print(sens.sensors)
    print(receiveDataOnSensors)


mqttBroker = 'broker.hivemq.com'
port = 1883
client = mqtt.Client('Python_Fernando')
client.connect(mqttBroker, port)
while 1:
    client.subscribe(topic_sub)
    client.on_message = on_message
    client.loop_forever()
