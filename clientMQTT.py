import json
import paho.mqtt.client as mqtt
from time import strftime, localtime, time
from DataBaseManager.OperationalDataBase import Sensors, DataBasePostgreSQL
from DataBaseManager.OperationalDataBase import DataSensors, LogErrorsMixin


class VerifySensors:
    def __init__(self, dbPostgreSQL: DataBasePostgreSQL) -> None:
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

    def getIdSensor(self, sensor) -> int:
        for i in self.__sensorsOnDataBase:
            if sensor == i[2]:
                return int(i[0])
        return -1


class MQTTClient(LogErrorsMixin):
    def __init__(self, dbPostgreSQL: DataBasePostgreSQL) -> None:
        self.port = 1883
        self.mqttBroker = 'broker.hivemq.com'
        self.topic_sub = "ESP32_Sensors_BME280"

        self.receiveDataOnSensors: dict = {}

        self.client = mqtt.Client()
        self.sens = VerifySensors(dbPostgreSQL)
        self.sensData = DataSensors(dbPostgreSQL)

    def __on_message(self, client, userdata, msg):
        '''CallBack'''
        try:
            msgDecode = str(msg.payload.decode('utf-8', 'ignore'))
            receiveDataOnSensors: dict = json.loads(msgDecode)
            if receiveDataOnSensors['dataHora'] != 'No date':
                receiveDataOnSensors['dataHora'] = strftime(
                    '%d/%m/%Y %H:%M:%S', localtime(int(
                        receiveDataOnSensors['dataHora']
                    ))
                )
            else:
                receiveDataOnSensors['dataHora'] = strftime(
                    '%d/%m/%Y %H:%M:%S', localtime(time())
                )
            if receiveDataOnSensors['IDMac'] not in self.sens.getSensorMac():
                self.sens.sensors = receiveDataOnSensors['IDMac']
            if self.sens.sensors:
                idSensor = self.sens.getIdSensor(receiveDataOnSensors['IDMac'])
                if idSensor != -1:
                    receiveDataOnSensors['id_sensor'] = idSensor
                    self.sensData.execInsertTable(
                        receiveDataOnSensors,
                        table='data_sensor',
                        collumn=(
                            'id_sensor', 'date_hour', 'temperature',
                            'humidity', 'pressure'
                        )
                    )

        except Exception as e:
            className = self.__class__.__name__
            methName = 'on_message'
            self.registerErrors(className, methName, e)

    def runMQTTClient(self):
        try:
            while 1:
                self.client.connect(self.mqttBroker, self.port)
                self.client.subscribe(self.topic_sub)
                self.client.on_message = self.__on_message
                self.client.loop_forever()
        except Exception as e:
            className = self.__class__.__name__
            methName = 'mqttClient'
            self.registerErrors(className, methName, e)


class Main:
    def __init__(self, db) -> None:
        self.dbPostgreSQL = DataBasePostgreSQL(db)
        self.mqttClient = MQTTClient(self.dbPostgreSQL)

    def run(self):
        self.mqttClient.runMQTTClient()
