import paho.mqtt.client as mqtt
from time import sleep


topic_pub = 'Require_Data'
msg = 'return'

mqttBroker = 'broker.hivemq.com'
port = 1883
client = mqtt.Client('Python')
client.connect(mqttBroker, port)
while 1:
    status = client.publish(topic_pub, msg)
    if status:
        print(msg)
    else:
        print('falhou msg')
    sleep(60)
