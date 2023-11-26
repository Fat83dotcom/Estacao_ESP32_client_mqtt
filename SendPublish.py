import paho.mqtt.client as mqtt
from daemonize import Daemonize
from time import sleep


pid = '/tmp/SendPublish.pid'


def main():
    topic_pub = 'Require_Data'
    msg = 'return'

    mqttBroker = 'broker.hivemq.com'
    port = 1883
    client = mqtt.Client()
    client.connect(mqttBroker, port)
    while 1:
        status = client.publish(topic_pub, msg)
        if status:
            print(msg)
        else:
            print('falhou msg')
        sleep(60)


daemon = Daemonize(app='SendPublish', pid=pid, action=main)
daemon.start()
