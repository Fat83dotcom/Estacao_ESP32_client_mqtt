import json
from abc import ABC, abstractmethod
from time import sleep
import paho.mqtt.client as mqtt
from time import strftime, localtime, time
from DataBaseManager.OperationalDataBase import Sensors, DataBasePostgreSQL
from DataBaseManager.OperationalDataBase import DataSensors, LogErrorsMixin
from DataBaseManager.settings_db import banco


class DBInterface(ABC):
    @abstractmethod
    def select(self) -> list: pass

    @abstractmethod
    def insert(self, *args) -> None: pass


class ConcreteSensor(DBInterface):
    def __init__(self, dbPostgreSQL: DataBasePostgreSQL) -> None:
        super().__init__()
        self.sensorsInstace = Sensors(dbPostgreSQL)

    def select(self) -> list:
        result: list = self.sensorsInstace.execSelectOnTable(
            table='Core_sensor',
            collCodiction='mac',
            condiction='',
            conditionLiteral='',
        )
        return [] if result is None else result

    def insert(self, *args) -> None:
        self.sensorsInstace.execInsertTable(
            *args,
            table='Core_sensor',
            collumn=('mac',),
        )


class ConcreteSensorData(DBInterface):
    def __init__(self, dbPostgreSQL: DataBasePostgreSQL) -> None:
        super().__init__()
        self.dataSensorInstance = DataSensors(dbPostgreSQL)

    def select(self) -> list:
        raise NotImplementedError('Não utilizado até agora...')

    def insert(self, *args) -> None:
        self.dataSensorInstance.execInsertTable(
            *args,
            table='Core_datasensor',
            collumn=(
                'id_sensor_id', 'date_hour', 'temperature',
                'humidity', 'pressure'
            )
        )


class DateHandler:
    def __init__(self) -> None:
        self.__dateEpoch: int = -1

    @property
    def dateEpoch(self):
        return self.__dateEpoch

    @dateEpoch.setter
    def dateEpoch(self, value):
        if isinstance(value, int):
            self.__dateEpoch = value

    def translateDate(self) -> str:
        if self.dateEpoch != -1:
            return strftime(
                '%d/%m/%Y %H:%M:%S', localtime(
                    self.dateEpoch
                )
            )
        else:
            return strftime(
                '%d/%m/%Y %H:%M:%S', localtime(time())
            )


class VerifySensors:
    def __init__(self, dbPostgreSQL: DataBasePostgreSQL) -> None:
        self.sensorsInstace = Sensors(dbPostgreSQL)
        self.__sensorsOnDataBase: list[tuple] = self.__getSensorsOnDB()
        self.__sensorMacs: list = self.__getSensorMacs(
            self.__sensorsOnDataBase
        )

    def __getSensorMacs(self, iterable: list) -> list:
        sensors = [
            mac[1] for mac in self.__sensorsOnDataBase
        ]
        return sensors

    def __getSensorsOnDB(self) -> list:
        sensors = [
            sens for sens in self.__searchSensors()
        ]
        return sensors

    @property
    def sensors(self):
        return self.__sensorsOnDataBase

    @sensors.setter
    def sensors(self, value):
        if isinstance(value, str):
            if len(self.__sensorsOnDataBase) == 0 or \
                    value not in self.__sensorMacs:
                self.__insertSensors(value)
                self.__sensorsOnDataBase: list[tuple] = self.__getSensorsOnDB()
                self.__sensorMacs: list = self.__getSensorMacs()
        raise ValueError(
            f'Verifique a entrada mac dos sensores! -> {value}'
        )

    def __searchSensors(self) -> list:
        result: list = self.sensorsInstace.execSelectOnTable(
            table='Core_sensor',
            collCodiction='mac',
            condiction='',
            conditionLiteral='',
        )
        return [] if result is None else result

    def __insertSensors(self, *args) -> None:
        self.sensorsInstace.execInsertTable(
            *args,
            table='Core_sensor',
            collumn=('mac',),
        )

    def getSensorMac(self) -> list:
        if self.__sensorMacs:
            return self.__sensorMacs
        else:
            return []

    def getIdSensor(self, sensor) -> int:
        for idSen in self.__sensorsOnDataBase:
            if sensor == idSen[1]:
                return int(idSen[0])
        return -1


class SensorHandler:
    def __init__(self, dbPostgreSQL: DataBasePostgreSQL) -> None:
        self.sensor = VerifySensors(dbPostgreSQL)
        self.__idSensor: str

    @property
    def idSensor(self):
        return self.__idSensor

    @idSensor.setter
    def idSensor(self, value):
        if isinstance(value, str):
            self.__idSensor = value

    def checkingSensors(self):
        if self.idSensor not in self.sensor.getSensorMac():
            self.sensor.sensors = self.idSensor

    def getIDSensor(self) -> int:
        if self.sensor.sensors:
            idSensor = self.sensor.getIdSensor(self.idSensor)
            return int(idSensor)
        return -1


class SubscribeMQTTClient(LogErrorsMixin):
    def __init__(self, dbPostgreSQL: DataBasePostgreSQL) -> None:
        self.port = 1883
        self.mqttBroker = 'broker.hivemq.com'
        self.topicSub = "ESP32_Sensors_BME280"

        self.client = mqtt.Client()
        self.sensorData = DataSensors(dbPostgreSQL)
        self.handleDate = DateHandler()
        self.handleSensor = SensorHandler(dbPostgreSQL)

    def __on_message(self, client, userdata, msg):
        '''CallBack'''
        try:
            msgDecode = str(msg.payload.decode('utf-8', 'ignore'))
            receiveDataOnSensors: dict = json.loads(msgDecode)
            self.handleDate.dateEpoch = receiveDataOnSensors['dataHora']
            self.handleSensor.idSensor = receiveDataOnSensors['IDMac']

            self.handleSensor.checkingSensors()
            idSensor: int = self.handleSensor.getIDSensor()

            if idSensor != -1:
                receiveDataOnSensors[
                    'dataHora'
                ] = self.handleDate.translateDate()
                receiveDataOnSensors['codS'] = idSensor
                self.sensorData.execInsertTable(
                    receiveDataOnSensors,
                    table='Core_datasensor',
                    collumn=(
                        'id_sensor_id', 'date_hour', 'temperature',
                        'humidity', 'pressure'
                    )
                )
        except Exception as e:
            className = self.__class__.__name__
            methName = 'on_message'
            self.registerErrors(className, methName, e)

    def run(self):
        while 1:
            try:
                self.client.connect(self.mqttBroker, self.port)
                self.client.subscribe(self.topicSub)
                self.client.on_message = self.__on_message
                self.client.loop_forever()
            except Exception as e:
                className = self.__class__.__name__
                methName = 'run'
                self.registerErrors(className, methName, e)


class PlublishMQTTClient:
    def __init__(self) -> None:
        self.port = 1883
        self.mqttBroker = 'broker.hivemq.com'
        self.topicPub = 'Require_Data'
        self.msg = 'return'

        self.client = mqtt.Client()

    def run(self) -> None:
        self.client.connect(self.mqttBroker, self.port)
        while 1:
            try:
                self.client.publish(self.topicPub, self.msg)
                sleep(60)
            except Exception as e:
                className = self.__class__.__name__
                methName = 'run'
                self.registerErrors(className, methName, e)


class Main(LogErrorsMixin):
    def __init__(self, clientMQTT) -> None:
        self.mqttClient = clientMQTT

    def run(self):
        try:
            self.mqttClient.run()
        except Exception as e:
            className = self.__class__.__name__
            methName = 'run'
            self.registerErrors(className, methName, e)
