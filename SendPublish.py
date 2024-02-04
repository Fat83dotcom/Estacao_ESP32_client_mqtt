from daemonize import Daemonize
from clientMQTT import Main, PlublishMQTTClient

pubClient = PlublishMQTTClient()
main = Main(pubClient)


pid = '/tmp/SendPublish.pid'
daemon = Daemonize(app='SendPublish', pid=pid, action=main.run)
daemon.start()
