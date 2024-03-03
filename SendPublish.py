from daemonize import Daemonize
from clientMQTT import Main, PlublishMQTTClient
from DataBaseManager.settings_db import credentialBorker

pubClient = PlublishMQTTClient(
    credentialBorker['user'], credentialBorker['password']
)
main = Main(pubClient)


pid = '/tmp/SendPublish.pid'
daemon = Daemonize(app='SendPublish', pid=pid, action=main.run)
daemon.start()
