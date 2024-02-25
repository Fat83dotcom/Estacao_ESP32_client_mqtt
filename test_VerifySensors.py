import unittest
from clientMQTT import VerifySensors, DBInterface


class FakeDB(DBInterface):
    def select(self) -> list:
        return [
            (1, 'e9:ae:05:9c:3d:75'), (2, '7c:33:50:0f:1f:dc'),
            (3, 'ab:8e:e6:d0:5e:cd')
        ]

    def insert(self, *args) -> None:
        pass


class Test_VerifySensors(unittest.TestCase):
    def setUp(self) -> None:
        self.db = FakeDB()
        self.vrSens = VerifySensors(self.db)

    def test_getSensorOnDB_Return_List_Of_Tuples(self):
        result = [
            (1, 'e9:ae:05:9c:3d:75'), (2, '7c:33:50:0f:1f:dc'),
            (3, 'ab:8e:e6:d0:5e:cd')
        ]
        self.assertEqual(self.vrSens.__getSensorsOnDB(), result)

    def test_Get_Sensors_Mac_Return_List_Macs(self):
        result = [
            'e9:ae:05:9c:3d:75', '7c:33:50:0f:1f:dc',
            'ab:8e:e6:d0:5e:cd'
        ]
        self.assertEqual(self.vrSens.__getSensorMacs(), result)

    def test_GetIdSensor_Return_Ids_From_Sensors(self):
        result: int = 2
        argument: str = '7c:33:50:0f:1f:dc'
        self.assertEqual(self.vrSens.getIdSensor(argument), result)

    def test_GetIdSensor_Return_Minus_1_For_Argument_Invalid(self):
        result: int = -1
        argument: str = '7c:3f:53:0f:5f:da'
        self.assertEqual(self.vrSens.getIdSensor(argument), result)

    def test_GetIdSensor_Many_Tests(self):
        result = [1, -1, 2, -1, 3, -1, -1]
        source = [
            'e9:ae:05:9c:3d:75', '7c:63:60:0a:1f:dc',
            '7c:33:50:0f:1f:dc', '7c:34:50:08:7f:a9',
            'ab:8e:e6:d0:5e:cd', 'ab:5e:e6:f0:ff:cd',
            'ab:8a:e2:55:aa:ff',
        ]
        for n, mac in enumerate(source):
            with self.subTest(source=mac, result=result[n]):
                self.assertEqual(self.vrSens.getIdSensor(mac), result[n])
