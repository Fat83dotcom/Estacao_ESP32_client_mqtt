import json
from time import sleep
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

    def __searchSensors(self) -> list:
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
                receiveDataOnSensors['id_sensor'] = idSensor
                self.sensorData.execInsertTable(
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

    def run(self):
        try:
            while 1:
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
        try:
            self.client.connect(self.mqttBroker, self.port)
            while 1:
                self.client.publish(self.topicPub, self.msg)
                sleep(60)
        except Exception as e:
            className = self.__class__.__name__
            methName = 'run'
            self.registerErrors(className, methName, e)


class Main:
    def __init__(self, clientMQTT) -> None:
        self.mqttClient = clientMQTT

    def run(self):
        self.mqttClient.run()
