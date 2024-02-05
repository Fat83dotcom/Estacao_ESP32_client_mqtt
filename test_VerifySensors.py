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
        self.assertEqual(self.vrSens._getSensorsOnDB(), result)
