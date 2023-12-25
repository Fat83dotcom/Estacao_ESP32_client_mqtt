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
                    sQL, data = query
                    cursor.execute(sQL, data)
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
                    sQL, data = query
                    cursor.execute(sQL, data)
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
        try:
            values = args[0]
            query: tuple = sql.SQL(
                "INSERT INTO {table} ({collumn}) VALUES ({pHolders})"
            ).format(
                table=sql.Identifier(schema, table),
                collumn=sql.SQL(', ').join(map(sql.Identifier, collumn)),
                pHolders=sql.SQL(', ').join(sql.Placeholder() * len(collumn))
            ), values
            return query
        except (Error, Exception) as e:
            className = self.__class__.__name__
            methName = self.SQLInsertGenerator.__name__
            self.registerErrors(className, methName, e)
            raise e

    def SQLUpdateGenerator(
            self, *args, collumnUpdate: str, collumnCondicional: str,
            table: str, schema: str, update: str, conditionalValue: str
            ):
        try:
            query = sql.SQL(
                "UPDATE {table} SET {colUp}=%s WHERE {colCon}=%s"
            ).format(
                table=sql.Identifier(schema, table),
                colUp=sql.Identifier(collumnUpdate),
                colCon=sql.Identifier(collumnCondicional)
            ), (update, conditionalValue)
            return query
        except (Error, Exception) as e:
            className = self.__class__.__name__
            methName = self.SQLUpdateGenerator.__name__
            self.registerErrors(className, methName, e)
            raise e

    def SQLDeleteGenerator(self) -> tuple:
        return ('Não Implementado !!',)

    def SQLSelectGenerator(
        self, table: str, collCodiction: str, condiction: str,
        schema: str, collumns: tuple, conditionLiteral: str
    ) -> tuple:
        try:
            if conditionLiteral == '' and condiction == '':
                if '*' in collumns:
                    query = sql.SQL(
                        """SELECT * FROM {tab}"""
                    ).format(
                        tab=sql.Identifier(schema, table),
                    ), ()
                    return query
                else:
                    query = sql.SQL(
                        """SELECT {col} FROM {tab}"""
                    ).format(
                        col=sql.SQL(', ').join(map(sql.Identifier, collumns)),
                        tab=sql.Identifier(schema, table),
                    ), ()
                    return query
            elif conditionLiteral == '':
                if '*' in collumns:
                    query = sql.SQL(
                        """SELECT * FROM {tab}
                            WHERE {colCond}={cond}"""
                    ).format(
                        tab=sql.Identifier(schema, table),
                        colCond=sql.Identifier(collCodiction),
                        cond=sql.Literal(condiction)
                    ), ()
                    return query
                else:
                    query = sql.SQL(
                        """SELECT {col} FROM {tab}
                            WHERE {colCond}={cond}"""
                    ).format(
                        col=sql.SQL(', ').join(map(sql.Identifier, collumns)),
                        tab=sql.Identifier(schema, table),
                        colCond=sql.Identifier(collCodiction),
                        cond=sql.Identifier(condiction)
                    ), ()
                    return query
            else:
                if '*' in collumns:
                    query = sql.SQL(
                        "SELECT * FROM {tab}" + f" {conditionLiteral}"  # type: ignore
                    ).format(
                        tab=sql.Identifier(schema, table)
                    ), ()
                    return query
                else:
                    query = sql.SQL(
                        "SELECT {col} FROM {tab}" + f" {conditionLiteral}"  # type: ignore
                    ).format(
                        col=sql.SQL(', ').join(map(sql.Identifier, collumns)),
                        tab=sql.Identifier(schema, table),
                    ), ()
                    return query
        except (Error, Exception) as e:
            className = self.__class__.__name__
            methName = self.SQLUpdateGenerator.__name__
            self.registerErrors(className, methName, e)
            raise e

    def updateTable(
        self, table: str, collumnUpdate: str,
        collumnCondicional: str, update: str,
        conditionalValue: str, schema='public',
    ) -> None:
        '''
            Atualiza colunas.
            Parametros: collumn -> Nome da coluna
            condition -> Condição de atualização
            update -> Valor da modificação
        '''
        try:
            query = self.SQLUpdateGenerator(
                table=table, collumnUpdate=collumnUpdate,
                collumnCondicional=collumnCondicional,
                schema=schema, update=update,
                conditionalValue=conditionalValue
            )
            self.toExecute(query)
        except (Error, Exception) as e:
            raise e

    def insertTable(
        self, *args, table: str, collumn: tuple, schema='public'
    ) -> None:
        '''
            Insere dados na tabela.
            Parametros:
            *args -> tupla com os valores, em ordem com a coluna
            collumn -> Nome das colunas, na ordem de inserção.
        '''
        try:
            query: tuple = self.SQLInsertGenerator(
                *args, table=table, collumn=collumn, schema=schema
            )
            self.toExecute(query)
        except (Error, Exception) as e:
            raise e

    def deleteOnTable(self) -> None:
        pass

    def selectOnTable(
        self, table: str, collCodiction: str, condiction: str,
        conditionLiteral: str, schema='public', collumns=('*',)
    ) -> list:
        try:
            query = self.SQLSelectGenerator(
                table=table, collCodiction=collCodiction,
                condiction=condiction, schema=schema,
                collumns=collumns, conditionLiteral=conditionLiteral
            )
            return self.toExecuteSelect(query)
        except (Error, Exception) as e:
            raise e


class DataModel(ABC, LogErrorsMixin):
    '''
        Implementa uma interface para receber os dados e realiza as
        transações para cada tabela do banco.
    '''
    def __init__(self, dB: DataBasePostgreSQL) -> None:
        self.DBInstance = dB

    def execInsertTable(
        self, *args, table: str, collumn: tuple, schema='public'
    ) -> None:
        '''
            Implementa uma estrutura pra inserir dados em tabelas.
            Retorna -> None
        '''
        raise NotImplementedError('Implemente o metodo em uma subclasse'
                                  ' relativa a tabela trabalhada.')

    def execCreateTable(
        self, *args, tableName: str, schema='public'
    ) -> None:
        '''
            Implementa uma estrutura para criar tabelas.
            Retorna -> None
        '''
        raise NotImplementedError('Implemente o metodo em uma subclasse'
                                  ' relativa a tabela trabalhada.')

    def execUpdateTable(
        self, table: str, collumnUpdate: tuple, collumnCondicional: str,
        update: str, conditionalValue: str, schema='public',
    ) -> None:
        '''
            Implementa uma estrutura para atualizar tabelas.
            Retorna -> None
        '''
        raise NotImplementedError('Implemente o metodo em uma subclasse'
                                  ' relativa a tabela trabalhada.')

    def execDeleteOnTable(self, table: str, key: str) -> None:
        '''
            Implementa uma estrutura para deletar linhas em tabelas.
            Retorna -> None
        '''
        raise NotImplementedError('Implemente o metodo em uma subclasse'
                                  ' relativa a tabela trabalhada.')

    def execSelectOnTable(
        self, table: str, collCodiction: str, condiction: str,
        conditionLiteral: str, schema='public', collumns=('*', )
    ) -> list:
        '''
            Implementa uma estrutura para criar buscar dados em tabelas.
            Retorna -> None
        '''
        raise NotImplementedError('Implemente o metodo em uma subclasse'
                                  ' relativa a tabela trabalhada.')


class Sensors(DataModel):
    def __init__(self, dB: DataBasePostgreSQL) -> None:
        super().__init__(dB)

    def execSelectOnTable(
        self, table: str, collCodiction: str,
        condiction: str, conditionLiteral: str,
        schema='public', collumns=('*', )
    ) -> list:
        try:
            result: list = self.DBInstance.selectOnTable(
                table=table, collCodiction=collCodiction,
                condiction=condiction, conditionLiteral=conditionLiteral,
                collumns=collumns
            )
            return result
        except Exception as e:
            print(e)

    def execInsertTable(
        self, *args, table: str, collumn: tuple, schema='public'
    ) -> bool:
        try:
            data = (
                args[0],
            )
            self.DBInstance.insertTable(
                data, table=table, collumn=collumn
            )
            return True
        except Exception as e:
            print(e)
            return False


class DataSensors(DataModel):
    def __init__(self, dB: DataBasePostgreSQL) -> None:
        super().__init__(dB)

    def execInsertTable(
        self, *args, table: str, collumn: tuple, schema='public'
    ) -> None:
        data = (
            args[0]['codS'],
            args[0]['dataHora'],
            args[0]['Temperatura'],
            args[0]['Umidade'],
            args[0]['Pressao']
        )
        self.DBInstance.insertTable(
            data,
            table=table,
            collumn=collumn
        )


if __name__ == '__main__':

    pass
