from kafka import KafkaConsumer
import json,os


# Kafka broker address and topic name
#brokers = os.environ.get('KAFKA_BROKER')
brokers = 'localhost'
topic = 'wenglor_to_kafka'

# Create a Kafka consumer
consumer = KafkaConsumer(topic,
                         bootstrap_servers=brokers,
                         group_id='my-group',
                         auto_offset_reset='latest',
                         enable_auto_commit=False)

last_time = 0
try:
    while True:  # Continue running indefinitely
        #for message in consumer:
            # # 解析消息的键和值
            # key = message.key
            # value = json.loads(message.value)
            
            # # 获取每个数组的第一个值
            # x_first_value = value['x'][0] if 'x' in value else None
            # z_first_value = value['z'][0] if 'z' in value else None
            # i_first_value = value['i'][0] if 'i' in value else None
            # w_first_value = value['w'][0] if 'w' in value else None
            
            # # 显示消息的键和每个数组的第一个值
            #print(f"Key: {key}, x[0]: {x_first_value}, z[0]: {z_first_value}, i[0]: {i_first_value}, w[0]: {w_first_value}")
        for message in consumer:
            key = message.key # Decode the message key
            value = json.loads(message.value)  # Decode and parse the message value as JSON

            #print(key)
            # Extract the first value of int I, double X, and double Z arrays
            if 'I' in value and len(value['I']) > 0:
                first_I = value['I'][0]
            else:
                first_I = None

            if 'X' in value and len(value['X']) > 0:
                first_X = value['X'][0]
            else:
                first_X = None

            if 'Z' in value and len(value['Z']) > 0:
                first_Z = value['Z'][0]
            else:
                first_Z = None
                
            #print(f"{key}, First I: {first_I}, First X: {first_X}, First Z: {first_Z}")

            #current = time.time()

            #humentime = datetime.datetime.fromtimestamp(int(key)/1000)
            print(f"{key}, First I: {first_I}, First X: {first_X}, First Z: {first_Z}")
            # if current - last_time >= 1:
            #     humentime = datetime.datetime.fromtimestamp(int(key)/1000)
            #     print(f"{humentime},  First I: {first_I}, First X: {first_X}, First Z: {first_Z}")
            #    last_time = current

except KeyboardInterrupt:
    pass

finally:
    consumer.close()

