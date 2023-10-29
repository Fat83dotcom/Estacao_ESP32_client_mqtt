from paho.mqtt import client as mqtt_client
import logging
import time

broker = 'broker.hivemq.com'
port = 1883
topic_sub_temp = 'ESP32_Sensors_BME280_TEMP'
topic_sub_press = 'ESP32_Sensors_BME280_PRESS'
topic_sub_humi = 'ESP32_Sensors_BME280_HUMI'
topic_pub = 'ESP32_Receive_Information'
client_id = 'Python'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info(
        "Reconnect failed after %s attempts. Exiting...", reconnect_count
    )


def publish(client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic_pub, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic_pub}`")
        else:
            print(f"Failed to send message to topic {topic_pub}")
        msg_count += 1
        if msg_count > 5:
            break


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(
            f"Received {msg.payload.decode('utf-8')} from {msg.topic} topic"
        )

    client.subscribe(topic_sub_temp)
    client.subscribe(topic_sub_press)
    client.subscribe(topic_sub_humi)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    while 1:
        subscribe(client)
        client.loop_forever()


if __name__ == '__main__':
    run()