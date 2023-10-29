import paho.mqtt.client as mqtt
import json


topic_sub = "ESP32_Sensors_BME280"


def on_message(client, userdata, msg):
    msgDecode = str(msg.payload.decode('utf-8', 'ignore'))
    msgJson = json.loads(msgDecode)
    print(msgJson)


mqttBroker = 'broker.hivemq.com'
port = 1883
client = mqtt.Client('Python_Fernando')
client.connect(mqttBroker, port)
while 1:
    client.subscribe(topic_sub)
    client.on_message = on_message
    client.loop_forever()
