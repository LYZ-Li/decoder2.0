# import paho.mqtt.client as mqtt
# import time
# import os

# ## Mosquitto 
# mqttBroker = "localhost"
# mqttPort = 1883
# mqttTopic = "wenglor_trigger"


# client = mqtt.Client("publisher")

# client.connect(os.environ.get("MQTT_IP",mqttBroker),os.environ.get("MQTT_PORT",mqttPort))

# trigger = True
# client.publish(mqttTopic, trigger)

# time.sleep(1)

# trigger = False
# client.publish(mqttTopic, trigger)

# client.disconnect()



import time
trigger = False

def main():
    wenglorInit()
    trigger = True
    wenglor(trgger)
    time.sleep(5)
