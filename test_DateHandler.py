import unittest
from clientMQTT import DateHandler
from time import strftime, localtime, time


class Test_Translate_Date(unittest.TestCase):
    def setUp(self) -> None:
        self.dtHandler = DateHandler()

    def test_Translate_Date_Return_Correct_Date(self):
        source: int = 1707072990
        self.dtHandler.dateEpoch = source
        self.assertEqual(self.dtHandler.translateDate(), '04/02/2024 15:56:30')

    def test_Translate_Date_Return_Correct_Many_Dates(self):
        manysource: list = [
            1707063650, 1707063717, 1707063734
        ]
        manyResult: list = [
            '04/02/2024 13:20:50', '04/02/2024 13:21:57',
            '04/02/2024 13:22:14',
        ]
        for n, source in enumerate(manysource):
            self.dtHandler.dateEpoch = source
            with self.subTest(source=source, manyResult=manyResult[n]):
                self.assertEqual(
                    self.dtHandler.translateDate(), manyResult[n]
                )

    def test_Translate_Date_Return_System_Date(self):
        source: int = -1
        self.dtHandler.dateEpoch = source
        self.assertEqual(
            self.dtHandler.translateDate(),
            strftime(
                '%d/%m/%Y %H:%M:%S', localtime(time())
            )
        )


if __name__ == '__main__':
    unittest.main()
