import sys
from paho.mqtt import client as mqtt_client

broker = 'localhost'
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

    # msg_count = 0
    # while True:
    #     time.sleep(1)
    #     msg = f"messages: {msg_count}"
    #     result = client.publish(topic, msg_count)
    #     # result: [0, 1]
    #     status = result[0]
    #     if status == 0:
    #         print(f"Send `{msg}` to topic `{topic}`")
    #     else:
    #         print(f"Failed to send message to topic {topic}")
    #     msg_count += 1


def run():
    client = connect_mqtt()
    client.loop_start()
    while True:
        try:
            user_input = input("Enter 0 for 'False' or 1 for 'True': ")
            if user_input == '0':
                publish(client, "False")
            elif user_input == '1':
                publish(client, "True")
            else:
                print("Invalid input! Please enter 0 or 1.")
        except KeyboardInterrupt:
            print("\nExiting...")
            client.disconnect()
            sys.exit(0)

if __name__ == '__main__':
    run()