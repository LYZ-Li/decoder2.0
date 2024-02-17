import sys, time
from paho.mqtt import client as mqtt_client
import logging,sys
logging.basicConfig(stream=sys.stdout)

#broker = 'localhost'
broker = 'mosquitto'
port = 1883
topic = "/python/mqtt"
client_id = f'pesudo-main'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client,msg):
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

    # while True:
    #     time.sleep(10)
    #     msg = f"True"
    #     result = client.publish(topic, msg)
    #     # result: [0, 1]
    #     status = result[0]
    #     if status == 0:
    #         print(f"Send `{msg}` to topic `{topic}`")
    #     else:
    #         print(f"Failed to send message to topic {topic}")
    #     time.sleep(10)
    #     msg = f"False"
    #     result = client.publish(topic, msg)
    #     # result: [0, 1]
    #     status = result[0]
    #     if status == 0:
    #         print(f"Send `{msg}` to topic `{topic}`")
    #     else:
    #         print(f"Failed to send message to topic {topic}")



def run():
    client = connect_mqtt()
    #client.loop_start()
    while True:
        try:
            time.sleep(10)
            msg = f"True"
            client.publish(topic, msg)

            time.sleep(10)
            msg = f"False"
            client.publish(topic, msg)
        except KeyboardInterrupt:
            print("\nExiting...")
            client.disconnect()
            sys.exit(0)

if __name__ == '__main__':
    run()