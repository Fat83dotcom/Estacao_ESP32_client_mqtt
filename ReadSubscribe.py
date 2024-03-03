from daemonize import Daemonize
from DataBaseManager.settings_db import banco, credentialBorker
from DataBaseManager.OperationalDataBase import DataBasePostgreSQL
from clientMQTT import Main, SubscribeMQTTClient

dbPostgreSQL = DataBasePostgreSQL(banco)
subClient = SubscribeMQTTClient(
    dbPostgreSQL, credentialBorker['user'], credentialBorker['password']
)
main = Main(subClient)


pid = '/tmp/ReadSubscribe.pid'
daemon = Daemonize(app='ReadSubscribe', pid=pid, action=main.run)
daemon.start()
