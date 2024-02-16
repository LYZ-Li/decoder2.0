from kafka import KafkaProducer
import time
import json
from kafka import KafkaConsumer
import psycopg2
 

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
 
def split_data(data):
    data_list = data.split(';')
    timestamp = ""
    if len(data_list) >= 0:
        timestamp = data_list[0].strip()
 
    Z_str = [json.dumps([data_list[i].strip()], indent=None) for i in range(1, len(data_list), 4)]
    I_str = [json.dumps([data_list[i+1].strip()], indent=None) for i in range(1, len(data_list), 4)]
    PW_str = [json.dumps([data_list[i+2].strip()], indent=None) for i in range(1, len(data_list), 4)]
    X_str = [json.dumps([data_list[i+3].strip()], indent=None) for i in range(1, len(data_list), 4)]
       
    print(timestamp, Z_str, I_str, PW_str, X_str)
 
    return timestamp, Z_str, I_str, PW_str, X_str

def send_data_to_kafka(producer, topic, timestamp, Z_str, I_str, PW_str, X_str):
    # send timestamp
    print('entry')
    producer.send(topic, key=b'timestamp', value=timestamp.encode('utf-8')).add_callback(delivery_report)
    print('timestamp')
    # send Z, I, PW, X coordinates data
    producer.send(topic, key=b'Value_Z', value=str(Z_str).encode('utf-8')).add_callback(delivery_report)
    producer.send(topic, key=b'Value_I', value=str(I_str).encode('utf-8')).add_callback(delivery_report)
    print(I_str)
    producer.send(topic, key=b'Value_PW', value=str(PW_str).encode('utf-8')).add_callback(delivery_report)
    producer.send(topic, key=b'Value_X', value=str(X_str).encode('utf-8')).add_callback(delivery_report)
    print('Value_X')
    # Ensure all messages are sent
    producer.flush()
    print('flush')

def consume_data_from_kafka(consumer , topic):
    key_list = []
    value_list = []
    print('entry consume')
    consumer.subscribe([topic])
    print('subscribe ok')
    messages = consumer.poll(timeout_ms=3250)
    #print(messages)
    #for partition, message in consumer:
    for partition , message in messages.items():
        print('entry for')
        for record in message:
            key = record.key
            value = record.value
            partition = record.partition
            print(f"Received message: key={key}, value={value}, partition={partition}")
            key_list.append(key)
            #print(key_list)
            value_list.append(value)
            #print(value_list)
        consumer.commit()
    #consumer.close()
    #print('consumer close')
    return key_list, value_list
 
#def inPostgresql(keys , values):
def inPostgresql():
    pg_conn = psycopg2.connect(
        host = 'localhost',
        port = '5432',
        user = 'SmartWelding',
        password = 'notsosecret',
        dbname = 'SmartWelding',
    )
    pg_cursor = pg_conn.cursor()

    ver = "SELECT VERSION()"
    pg_cursor.execute(ver)
    data = pg_cursor.fetchone()
    print("database version : %s " % data)



    #create = """CREATE TABLE studenten (
    """         id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        age INTEGER,
        grade FLOAT
        )"""
    """pg_cursor.execute(create)
    print('table created')
    pg_conn.commit() """ 

    sqll ="INSERT INTO studenten (name) VALUES (%s)"
    #params = (101 , 'zszxz')
    # 执行语句

    pg_cursor.execute(sqll, ('John',))
    print("insert successfully")
    pg_conn.commit()
    print('pg_commit')

    """ for key, value in zip(keys, values):
        pg_cursor.execute("INSERT INTO IOTBOX (key, value) VALUES (%s, %s)",(key , value))
        print('pg_insert succeed')
        pg_conn.commit()
        print('Commit')
    #pg_cursor.execute(f"INSERT INTO IOT-BOX (key, value) VALUES (%s, %s)",(keys, values))
    print('pg_insert succeed') """

    pg_cursor.execute("SELECT * FROM studenten;")
    print('select begin')
    # 获取查询结果的所有行
    rows = pg_cursor.fetchall()

    # 打印查询结果
    for row in rows:
        print(row)
    pg_cursor.close()
    pg_conn.close()


if __name__ == "__main__":
    bootstrap_servers = '127.0.0.1:9092'
    kafka_topic = 'IOT-BOX'
    data = '2023-12-18 14:05:17;67.78745143288751;81.88804860877886;69.59672024357036;20.162918523111106;97.43277569661389;17.038767831685476;17.27869905124300;4.368104288891184;95.22337911198052;59.83082300059753;24.49933087868953;87.53867215196898;13.997406866749495;70.14994127817843;91.09169725561686;28.055150521345773'
    producer_config = {
        'bootstrap_servers': bootstrap_servers,
        # Add other configurations here
    }
 
    timestamp, Z_str, I_str, PW_str, X_str = split_data(data)
    print('split succeed')
    # Using KafkaProducer from kafka-python
    producer = KafkaProducer(**producer_config)
    print('producer')
    # Send all data to Kafka
    send_data_to_kafka(producer, kafka_topic, timestamp, Z_str, I_str, PW_str, X_str)
    print('send succeed')


    consumer = KafkaConsumer(
        'IOT-BOX',
        bootstrap_servers='127.0.0.1:9092',
        group_id='5',
        auto_offset_reset='earliest',  # 从最早的消息开始消费
    )

    consume_data_from_kafka(consumer, kafka_topic)
    print('consume succeed')

    key, value = consume_data_from_kafka(consumer, kafka_topic)

    #inPostgresql(key , value)
    inPostgresql()
    print('inPostgresql')

    consumer.close()



