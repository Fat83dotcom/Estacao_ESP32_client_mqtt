import json
from time import sleep
import paho.mqtt.client as mqtt
from abc import ABC, abstractmethod
from time import strftime, localtime, time
from DataBaseManager.settings_db import banco
from DataBaseManager.OperationalDataBase import DataBase
from DataBaseManager.OperationalDataBase import Sensors, DataBasePostgreSQL
from DataBaseManager.OperationalDataBase import DataSensors, LogErrorsMixin


class DBInterface(ABC):
    @abstractmethod
    def select(self) -> list: pass

    @abstractmethod
    def insert(self, *args) -> None: pass


class ConcreteSensor(DBInterface):
    def __init__(self, dbPostgreSQL: DataBase) -> None:
        super().__init__()
        self.sensorsInstace = Sensors(dbPostgreSQL)

    def select(self) -> list:
        result: list = self.sensorsInstace.execSelectOnTable()
        return [] if result is None else result

    def insert(self, *args) -> None:
        self.sensorsInstace.execInsertTable(*args)


class ConcreteSensorData(DBInterface):
    def __init__(self, dbPostgreSQL: DataBase) -> None:
        super().__init__()
        self.dataSensorInstance = DataSensors(dbPostgreSQL)

    def select(self) -> list:
        raise NotImplementedError('Não utilizado até agora...')

    def insert(self, *args) -> None:
        self.dataSensorInstance.execInsertTable(*args)


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
        return strftime(
            '%d/%m/%Y %H:%M:%S', localtime(
                self.dateEpoch
            )
        ) if self.dateEpoch != -1 else strftime(
            '%d/%m/%Y %H:%M:%S', localtime(time())
        )


class VerifySensors:
    def __init__(self, sqlManipulation: DBInterface) -> None:
        self.__select = sqlManipulation.select
        self.__insert = sqlManipulation.insert
        self.__sensorsOnDataBase: list[tuple] = self._getSensorsOnDB()

    def _getSensorsOnDB(self) -> list:
        return self.__select()

    def _getSensorMacs(self) -> list:
        return [
            mac[1] for mac in self.__sensorsOnDataBase
        ]

    @property
    def sensors(self):
        return self.__sensorsOnDataBase

    @sensors.setter
    def sensors(self, value):
        if isinstance(value, str):
            self.__sensorsOnDataBase: list[tuple] = self._getSensorsOnDB()
            if value not in self.getSensorMac():
                self.__insert(value)

    def getSensorMac(self) -> list:
        if self._getSensorMacs():
            return self._getSensorMacs()
        return []

    def getIdSensor(self, mac) -> int:
        for sensor in self.__sensorsOnDataBase:
            if mac == sensor[1]:
                print(mac)
                return int(sensor[0])
        return -1


class SensorHandler:
    def __init__(self, sqlManipulation: DBInterface) -> None:
        self.sensor = VerifySensors(sqlManipulation)
        self.__idSensor: str

    @property
    def macSensor(self):
        return self.__idSensor

    @macSensor.setter
    def macSensor(self, value):
        if isinstance(value, str):
            self.__idSensor = value

    def checkingSensors(self):
        if self.macSensor not in self.sensor.getSensorMac():
            self.sensor.sensors = self.macSensor

    def getIDSensor(self) -> int:
        if self.sensor.sensors:
            idSensor = self.sensor.getIdSensor(self.macSensor)
            return int(idSensor)
        return -1


class SubscribeMQTTClient(LogErrorsMixin):
    def __init__(self, dbPostgreSQL: DataBase) -> None:
        self.port = 1883
        self.mqttBroker = 'broker.emqx.io'
        self.topicSub = "ESP32_Sensors_BME280"

        self.client = mqtt.Client()
        self.concreteSensor = ConcreteSensor(dbPostgreSQL)
        self.concreteSensorData = ConcreteSensorData(dbPostgreSQL)
        self.handleSensor = SensorHandler(self.concreteSensor)
        self.handleDate = DateHandler()

    def __dataPersistent(self, data: dict) -> None:
        try:
            self.handleDate.dateEpoch = data['dataHora']
            self.handleSensor.macSensor = data['IDMac']

            self.handleSensor.checkingSensors()
            idSensor: int = self.handleSensor.getIDSensor()

            if idSensor != -1:
                data[
                    'dataHora'
                ] = self.handleDate.translateDate()
                data['codS'] = idSensor
                self.concreteSensorData.insert(data)
        except Exception as e:
            raise e

    def __on_message(self, client, userdata, msg):
        '''CallBack para Receber a Mensagem.'''
        try:
            msgDecode = str(msg.payload.decode('utf-8', 'ignore'))
            receiveDataOnSensors: dict = json.loads(msgDecode)
            self.__dataPersistent(receiveDataOnSensors)
        except Exception as e:
            className = self.__class__.__name__
            methName = 'on_message'
            self.registerErrors(className, methName, e)

    def __on_connect(self, client, userdata, flags, rc):
        ''' CallBack para conectar ao Broker.'''
        self.client.subscribe(self.topicSub)

    def run(self):
        while 1:
            try:
                self.client.on_connect = self.__on_connect
                self.client.on_message = self.__on_message
                self.client.connect(self.mqttBroker, self.port)
                self.client.loop_forever()
            except Exception as e:
                className = self.__class__.__name__
                methName = 'run'
                self.registerErrors(className, methName, e)


class PlublishMQTTClient(LogErrorsMixin):
    def __init__(self) -> None:
        self.port = 1883
        self.mqttBroker = 'broker.emqx.io'
        self.topicPub = 'Require_Data'
        self.msg = 'return'

        self.client = mqtt.Client()

    def __on_connect(self, client, userdata, flags, rc):
        '''CallBack para conectar ao Broker.'''
        self.client.publish(self.topicPub, self.msg)

    def run(self) -> None:
        while 1:
            try:
                self.client.on_connect = self.__on_connect
                self.client.loop_start()
                self.client.connect(self.mqttBroker, self.port)
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


if __name__ == '__main__':
    try:
        dbPostgreSQL = DataBasePostgreSQL(banco)
        clientSub = SubscribeMQTTClient(dbPostgreSQL)
        # clientPub = PlublishMQTTClient()
        mainSub = Main(clientSub)
        # mainPub = Main(clientPub)
        mainSub.run()
        # mainPub.run()
    except Exception as e:
        print(e)
