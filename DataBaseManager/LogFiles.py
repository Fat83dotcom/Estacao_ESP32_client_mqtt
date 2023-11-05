import os
import time
from datetime import datetime


class LogFiles:
    def _recordFile(self, *args):
        '''
            Grava o log no arquivo.
        '''
        path: str = os.path.join(os.getcwd(), 'logFile.txt')
        with open(path, "a", encoding='utf-8') as file:
            file.write(f'{args[0]}\n')

    def registerTimeElapsed(self, timeInit: float, timeEnd: float):
        '''
            Registra no arquivo o tempo decorrido ente snapshotTimes.
        '''
        raise NotImplementedError('Implementar registerTimeElapsed')

    def snapshotTime(self):
        '''
            Retorna o tempo corrente em segundos desde Epoch.
        '''
        raise NotImplementedError('Implementar snapshotTime')

    def registerTimeLogStart(self):
        '''
            Registra o inicio de um evento.
        '''
        raise NotImplementedError('Implementar registerTimeLogStart')

    def registerTimeLogEnd(self):
        '''
            Registra o término de um evento.
        '''
        raise NotImplementedError('Implementar registerErrors')

    def registerErrors(self, className, methName, error):
        '''
            Registra os erros levantados em exceções.
        '''
        raise NotImplementedError('Implementar registerErrors')


class LogErrorsMixin(LogFiles):
    '''
        Implementa log de erros e exceções.
    '''
    def registerErrors(self, className, methName, error):
        register = {
            'className': className,
            'methName': methName,
            'error': error,
            'hour': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        self._recordFile(register)


class LogTimeMixin(LogFiles):
    '''
        Implementa métodos para controle de intervalos de tempo.
    '''
    def registerTimeElapsed(self, timeInit: float, timeEnd: float):
        totalTime = timeEnd - timeInit
        self._recordFile({'time elapsed: ': totalTime, 'Seconds': ''})

    def snapshotTime(self):
        return time.time()

    def registerTimeLogStart(self):
        register = {
            'dialog': '*** Inicio do processo ***',
            'startTime': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        }
        self._recordFile(register)

    def registerTimeLogEnd(self):
        register = {
            'dialog': '*** Final do processo ***',
            'endTime': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        }
        self._recordFile(register)
