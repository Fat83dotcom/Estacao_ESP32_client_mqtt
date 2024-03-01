import psycopg
from abc import ABC, abstractmethod
from psycopg import sql, Error
from DataBaseManager.LogFiles import LogErrorsMixin


class DataBase(ABC):
    '''Classe abstrata que fornece os serviços básicos
    para as operações do banco de dados, permitindo a implementação de
    diversos SGBD's.'''
    def __init__(self, dBConfig: dict) -> None:
        self.host: str = dBConfig['host']
        self.port: str = dBConfig['port']
        self.dbname: str = dBConfig['dbname']
        self.user: str = dBConfig['user']
        self.password: str = dBConfig['password']

    @abstractmethod
    def toExecute(self, query: tuple) -> None: pass

    @abstractmethod
    def toExecuteSelect(self, query) -> list: pass

    @abstractmethod
    def placeHolderSQLGenerator(self, values) -> str | None: pass

    @abstractmethod
    def SQLInsertGenerator(
        self, *args, collumn: tuple, table: str, schema: str
    ) -> tuple | None: pass

    @abstractmethod
    def SQLUpdateGenerator(
            self, *args, collumnUpdate: str, collumnCondicional: str,
            table: str, schema: str, update: str, conditionalValue: str
            ) -> tuple: pass

    @abstractmethod
    def SQLDeleteGenerator(self) -> tuple: pass

    @abstractmethod
    def SQLSelectGenerator(
        self, table: str, collCodiction: str, condiction: str,
        schema: str, collumns: tuple, conditionLiteral: str
    ) -> tuple: pass

    @abstractmethod
    def updateTable(
        self, table: str, collumnUpdate: str, collumnCondicional: str,
        update: str, conditionalValue: str, schema='public',
    ) -> None: pass

    @abstractmethod
    def insertTable(
        self, *args, table: str, collumn: tuple, schema='public'
    ) -> None: pass

    @abstractmethod
    def selectOnTable(
        self, table: str, collCodiction: str, condiction: str,
        conditionLiteral: str, schema='public', collumns=('*',)
    ) -> list: pass


class DataBasePostgreSQL(DataBase, LogErrorsMixin):
    '''Realiza as operações com o PostgreSQL'''
    def __init__(self, dBConfig: dict) -> None:
        self.host: str = dBConfig['host']
        self.port: str = dBConfig['port']
        self.dbname: str = dBConfig['dbname']
        self.user: str = dBConfig['user']
        self.password: str = dBConfig['password']

    def toExecute(self, query: tuple):
        '''
            Abre e fecha conexões, executa transações
            com segurança mesmo em casos de falha.
        '''
        try:
            with psycopg.connect(
                host=self.host, dbname=self.dbname,
                user=self.user, port=self.port,
                password=self.password
            ) as con:
                with con.cursor() as cursor:
                    sQL = query
                    cursor.execute(sQL)
        except (Error, Exception) as e:
            className = self.__class__.__name__
            methName = self.toExecute.__name__
            self.registerErrors(className, methName, e)
            raise e

    def toExecuteSelect(self, query) -> list:
        '''
            Abre e fecha conexões, executa transações de select
            com segurança mesmo em casos de falha.
        '''
        try:
            with psycopg.connect(
                host=self.host, dbname=self.dbname, user=self.user,
                port=self.port, password=self.password
            ) as con:
                with con.cursor() as cursor:
                    sQL = query
                    cursor.execute(sQL)
                    dataRecovery: list = [x for x in cursor.fetchall()]
                    return dataRecovery
        except (Error, Exception) as e:
            className = self.__class__.__name__
            methName = self.toExecute.__name__
            self.registerErrors(className, methName, e)
            raise e

    def placeHolderSQLGenerator(self, values) -> str | None:
        try:
            placeHolders: str = ''
            sizeValues = len(values)
            for n, _ in enumerate(values):
                if sizeValues == 1 or n == (sizeValues - 1):
                    placeHolders += '%s'
                else:
                    placeHolders += '%s, '
            return placeHolders
        except (Error, Exception) as e:
            className = self.__class__.__name__
            methName = self.placeHolderSQLGenerator.__name__
            self.registerErrors(className, methName, e)
            raise e

    def SQLInsertGenerator(
        self, *args, collumn: tuple, table: str, schema: str
    ) -> tuple:
        return ('Não Implementado !!',)

    def SQLUpdateGenerator(
            self, *args, collumnUpdate: str, collumnCondicional: str,
            table: str, schema: str, update: str, conditionalValue: str
            ):
        return ('Não Implementado !!',)

    def SQLDeleteGenerator(self) -> tuple:
        return ('Não Implementado !!',)

    def SQLSelectGenerator(
        self, table: str, collCodiction: str, condiction: str,
        schema: str, collumns: tuple, conditionLiteral: str
    ) -> tuple:
        return ('Não Implementado !!',)

    def updateTable(self, query: str) -> None:
        '''
            Atualiza colunas.
            Parametros: collumn -> Nome da coluna
            condition -> Condição de atualização
            update -> Valor da modificação
        '''
        try:
            self.toExecute(query)
        except (Error, Exception) as e:
            raise e

    def insertTable(self, query: str) -> None:
        '''
            Insere dados na tabela.
            Parametros:
            *args -> tupla com os valores, em ordem com a coluna
            collumn -> Nome das colunas, na ordem de inserção.
        '''
        try:
            self.toExecute(query)
        except (Error, Exception) as e:
            raise e

    def deleteOnTable(self) -> None:
        pass

    def selectOnTable(self, query: str) -> list:
        try:
            return self.toExecuteSelect(query)
        except (Error, Exception) as e:
            raise e


class DataModel(ABC, LogErrorsMixin):
    '''
        Implementa uma interface para receber os dados e realiza as
        transações para cada tabela do banco.
    '''
    def __init__(self, dB: DataBase) -> None:
        self.DBInstance = dB

    def execInsertTable(self, *args: str) -> None:
        '''
            Implementa uma estrutura pra inserir dados em tabelas.
            Retorna -> None
        '''
        raise NotImplementedError('Implemente o metodo em uma subclasse'
                                  ' relativa a tabela trabalhada.')

    def execCreateTable(self, *args: str) -> None:
        '''
            Implementa uma estrutura para criar tabelas.
            Retorna -> None
        '''
        raise NotImplementedError('Implemente o metodo em uma subclasse'
                                  ' relativa a tabela trabalhada.')

    def execUpdateTable(self, *args: str) -> None:
        '''
            Implementa uma estrutura para atualizar tabelas.
            Retorna -> None
        '''
        raise NotImplementedError('Implemente o metodo em uma subclasse'
                                  ' relativa a tabela trabalhada.')

    def execDeleteOnTable(self, *args: str) -> None:
        '''
            Implementa uma estrutura para deletar linhas em tabelas.
            Retorna -> None
        '''
        raise NotImplementedError('Implemente o metodo em uma subclasse'
                                  ' relativa a tabela trabalhada.')

    def execSelectOnTable(self, *args: str) -> list:
        '''
            Implementa uma estrutura para criar buscar dados em tabelas.
            Retorna -> None
        '''
        raise NotImplementedError('Implemente o metodo em uma subclasse'
                                  ' relativa a tabela trabalhada.')


class Sensors(DataModel):
    def __init__(self, dB: DataBase) -> None:
        super().__init__(dB)

    def execSelectOnTable(self, *args: str) -> list:
        try:
            query = 'SELECT "id_sen", "mac" FROM "Core_sensor";'
            result: list = self.DBInstance.selectOnTable(query)
            return result
        except Exception as e:
            raise e

    def execInsertTable(self, *args: str) -> None:
        try:
            mac: str = args[0]
            query = f'INSERT INTO "Core_sensor" (mac) VALUES(\'{mac}\');'
            self.DBInstance.insertTable(query)
        except Exception as e:
            raise e


class DataSensors(DataModel):
    def __init__(self, dB: DataBase) -> None:
        super().__init__(dB)

    def execInsertTable(self, *args) -> None:
        try:
            data = (
                args[0]['codS'],
                args[0]['dataHora'],
                args[0]['Temperatura'],
                args[0]['Umidade'],
                args[0]['Pressao']
            )
            query = f'''
            INSERT INTO "Core_datasensor"
            (date_hour, temperature, humidity, pressure, id_sensor_id)
            VALUES('{data[1]}', {data[2]}, {data[3]}, {data[4]}, {data[0]});
            '''
            self.DBInstance.insertTable(query)
        except Exception as e:
            raise e


if __name__ == '__main__':

    pass
