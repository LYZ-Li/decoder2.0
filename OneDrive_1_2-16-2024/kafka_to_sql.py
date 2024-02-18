from kafka import KafkaProducer
import time
import json
from kafka import KafkaConsumer
import psycopg2
# kafka config 设置于全局
""" consumer = KafkaConsumer(
    'IOT-BOX', #Topic_name
    bootstrap_servers='127.0.0.1:9092',
    group_id='5',
    auto_offset_reset='latest', 
)
    consumer.close() """
# sql config  设置于全局
""" pg_conn = psycopg2.connect(
    host = 'localhost',
    port = '5432',
    user = 'SmartWelding',
    password = 'notsosecret',
    dbname = 'SmartWelding',
)
pg_cursor = pg_conn.cursor() # set a cursor""" 
""" pg_cursor.close()  #close the cursor
    pg_conn.close() #close the connection """


def consume_data_from_kafka(consumer , topic): # one batch
    key_carrier = []  #create a carrier for keys
    value_carrier = [] #create a carrier for values
    consumer.subscribe([topic]) #subscribe kafka topic
    messages = consumer.poll(timeout_ms=200,max_message=2048) #get data from kafka, timeout=200ms, max_message=?

    for message in messages.items(): # search every message in data
        for record in message: # search every record in each message
            key = record.key # get key of each record
            value = record.value #get value of each record
            key_carrier.append(key) # collect all keys of this batch together
            value_carrier.append(value) # collect all values of this batch together
        consumer.commit() # commit
    return key_carrier, value_carrier # make these two  for other funcs available

def createtable(pg_cursor, table_name, pg_conn): # create a table in PostgreSQL
    pg_cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",[('profilsensor',)]) # check whether the table already exist
    beTable = pg_cursor.fetchone()[0] # set beTable as a bool. exist = true, false = False
    if  beTable: # if it exists, do nothing
        print('table already exist')  
    else: # if not exist yet, create a new one.
        #pg_cursor.execute("CREATE SEQUENCE welding_id_seq INCREMENT BY 1 START WITH 1 MINVALUE 1 NO MAXVALUE CACHE 2048;")  # ignore it 
        #pg_conn.commit()   #ignore it
        
        #create a sql command. This table has 5 columns. The first column records how many rows. The rest are timestamp, x, z and intensity, respectively
        table = """CREATE TABLE PROFILSENSOR(
        weldingNr SERIAL PRIMARY KEY,
        timestamp FLOAT,
        x FLOAT,
        Z FLOAT,
        intensity FLOAT
        )"""
        print('A new table have been created!') # print something
        pg_cursor.execute(table) # excute the sql command
        pg_conn.commit() # commit

def inPostgresql(pg_cursor, pg_conn, keys , values): #insert the data into SQL
    # insert keys into key-column
    for key in keys:
        insertonekey ="INSERT INTO PROFILSENSOR (timestamp) VALUES (%s)",(key) # create sql command
        pg_cursor.execute(insertonekey) # excute sql command
        pg_conn.commit()
    # insert x z i into their columns
    for json_data in values:
        x_value = json_data["x"] # get x from json
        z_value = json_data["z"] # get z from json
        i_value = json_data["i"] # get i from json
        insertxzi = f"INSERT INTO PROFILSENSOR (x, z, intensity) VALUES (%s, %s, %s)",(x_value,z_value,i_value) # create sql command
        pg_cursor.execute(insertxzi)
        pg_conn.commit()

