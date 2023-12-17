from daemonize import Daemonize
from DataBaseManager.settings_db import banco
from clientMQTT import Main

main = Main(banco)

pid = '/tmp/ReadSubscribe.pid'
daemon = Daemonize(app='ReadSubscribe', pid=pid, action=main.run)
daemon.start()
