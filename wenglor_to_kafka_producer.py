import ctypes
#import asyncio
from kafka.producer import KafkaProducer
import os, json, pytz
import time
from datetime import datetime
import threading
import queue
import paho.mqtt.client as mqtt
from kafka.errors import NoBrokersAvailable
import traceback

##################################_____________C++ interface_______________##############################

# Load the shared library
#lib = ctypes.CDLL("EthernetScanner/libEthernetScanner.so")  # Replace "your_library_name.so" with the actual name of your library
lib = ctypes.CDLL("/app/libEthernetScanner.so")  

# Define the argument and return types for the function
lib.EthernetScanner_Connect.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.EthernetScanner_Connect.restype = ctypes.c_void_p

lib.EthernetScanner_Disconnect.restype = ctypes.c_void_p
lib.EthernetScanner_Disconnect.argtypes = [ctypes.c_void_p]

lib.EthernetScanner_WriteData.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
lib.EthernetScanner_WriteData.restype = ctypes.c_int

lib.EthernetScanner_GetXZIExtended.restype = ctypes.c_int
lib.EthernetScanner_GetXZIExtended.argtypes = [
    ctypes.c_void_p,  # void* pEthernetScanner
    ctypes.POINTER(ctypes.c_double),  # double* pdoX
    ctypes.POINTER(ctypes.c_double),  # double* pdoZ
    ctypes.POINTER(ctypes.c_int),     # int* piIntensity
    ctypes.POINTER(ctypes.c_int),     # int* piSignalWidth
    ctypes.c_int,                      # int iBuffer
    ctypes.POINTER(ctypes.c_uint),    # unsigned int* puiEncoder
    ctypes.POINTER(ctypes.c_uint),    # unsigned int* pucUSRIO
    ctypes.c_int,                      # int dwTimeOut
    ctypes.POINTER(ctypes.c_ubyte),   # unsigned char* ucBufferRaw
    ctypes.c_int,                      # int iBufferRaw
    ctypes.POINTER(ctypes.c_int)      # int* iPicCnt
]

# global
iBuffer = 2048
pdoX = (ctypes.c_double* iBuffer)()
pdoZ = (ctypes.c_double* iBuffer)()
piIntensity = (ctypes.c_int * iBuffer)()
piSignalWidth = (ctypes.c_int * iBuffer)()
puiEncoder = ctypes.c_uint()
pucUSRIO = ctypes.c_uint()
dwTimeOut = 1000  # timeout value in milliseconds
ucBufferRaw = ctypes.c_ubyte()
iBufferRaw = 0  
iPicCnt = ctypes.c_int()

trigger = False
Queue = queue.Queue()

#######################################___________sensor_____________#########################
# def connect to sensor
def connect_to_sensor(ip, port, timeout):
    try:
        chIP = ip.encode("utf-8")
        chPort = port.encode("utf-8")
        handle = lib.EthernetScanner_Connect(chIP, chPort, timeout)
        if handle is None or handle == ctypes.cast(0, ctypes.c_void_p):
            raise Exception("Failed to connect to sensor")
        else:
            print("Sensor connected successfully. Handle:", handle)
            return handle
    except Exception as e:
        print("Connection failed. Error:", e)
        return None

# def initial sensor
def init_wenglor(pScanner):
    write_to_wenglor(pScanner,b'SetAcquisitionStop')
    time.sleep(1)
    write_to_wenglor(pScanner,b'SetAcquisitionLineTime=10000')# set frequency to 100Hz, on Instruction Page 115
    write_to_wenglor(pScanner,b'SetHeartBeat=x=1000')# set heartbeat 1000ms, on Instruction Page 120

def saveData(savePath,x,z,i,w):
    timestamp_ms = int(time.time() * 1000)

    with open(savePath, "a") as file:
        file.write(f"{timestamp_ms}\n")
        for x_val, z_val, i_val, w_val in zip(x, z, i, w):
            file.write(f"{x_val:.4f},{z_val:.4f},{i_val}\n")#,{w_val}\n")

def write_to_wenglor(pScanner, ascii_command):   
    command = ascii_command#.encode('utf-8')  # Convert ASCII command to bytes
    command_length = len(command)
    result = lib.EthernetScanner_WriteData(pScanner, command, command_length)
    # Check the result
    if result == command_length:
        return True  # Invalid handle
    else:
        return False  # Command sent successfully

def decoder(pScanner, savePath):
    write_to_wenglor(pScanner,b'SetAcquisitionStart')
    while trigger== 'True':
        result = lib.EthernetScanner_GetXZIExtended(
                pScanner, pdoX, pdoZ, piIntensity, piSignalWidth,
                iBuffer, puiEncoder, pucUSRIO, dwTimeOut, ucBufferRaw, iBufferRaw, iPicCnt
            )
        if result == -1:
            continue
        elif result > 0:
            timestamp = int(time.time() * 1000)
            xval = [value for value in pdoX]
            zval = [value for value in pdoZ]
            ival = [value for value in piIntensity]
            wval = [value for value in piSignalWidth]
            Queue.put([timestamp, xval,zval,ival,wval])
            saveData(savePath,pdoX, pdoZ, piIntensity, piSignalWidth, )
    
#####################################_____________kafka______________############################
class SubscriptionHandler:
    def __init__(self, producer):
        self.producer=producer

    def pack_send(self, t,x,z,i,w):
        # xval = [value for value in x]
        # zval = [value for value in z]
        # ival = [value for value in i]
        # wval = [value for value in w]
        data = {'x': x, 'z': z, 'i': i, 'w': w}
        val = json.dumps(data)
        key_bytes = str(t).encode()
        #self.producer.send('wenglor', {'key':int(time.time()*1000), 'value':val})#, 'timestamp':datetime.now(pytz.utc).isoformat()})
        try:
            self.producer.send('wenglor_to_kafka', key=key_bytes, value=val)#, timestamp= datetime.now(pytz.utc).isoformat())
            self.producer.flush()
        except Exception as e:
            print(f"Failed to send message: {e}")
            traceback.print_exc()
def sendKafka(producer):
    while trigger== 'True':
        if not Queue.empty():
            t,x,z,i,w = Queue.get()
            producer.pack_send(t,x,z,i,w)

########################################__________main____________#################################
## Mosquitto 
#mqttbroker = "localhost"
mqttbroker = "mosquitto"
mqttport = 1883
mqttTopic = "wenglor_trigger"

thread_stop = threading.Event()

#define connection callback
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"MQTT Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/python/mqtt")
    
def on_disconnect(client, userdata,rc):
    client.reconnect()

oldtrigger = None
threads = []
def on_message(client, userdata, message):
    global trigger
    global oldtrigger
    global threads 

    trigger = message.payload.decode('utf-8')
    print('')
    print('Received trgger:', trigger)
    if oldtrigger == trigger:
        return
    elif oldtrigger == None and trigger == 'False':
        oldtrigger = trigger
        return
    else:
        oldtrigger = trigger

    if trigger == "True":
        print('Starting data acquisition...')
        # filename
        current_time = datetime.now().strftime("%Y%m%d%H%M")
        savePath = f"{folder_name}/ScanData{current_time}.txt"

        thread_stop.clear() 
        thread_decoder = threading.Thread(target=decoder,args=(pEthernetScanner, savePath, ))
        thread_sendKafka = threading.Thread(target=sendKafka,args=(producer, ))
        threads =  [thread_decoder,thread_sendKafka]
        for thread in threads:
            thread.start()

    elif trigger == "False":
        oldtrigger = None
        print('Stopping data acquisition...')
        thread_stop.set()
        for thread in threads:
            if thread in locals() and thread.is_alive():
                thread.join()
        print('Data acquisition stopped.')
        write_to_wenglor(pEthernetScanner,b'SetAcquisitionStop')

def mqttListening(mqttbroker,mqttport):
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                        client_id="client-001",
                        clean_session=False)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect=on_disconnect
    mqttc.reconnect_delay_set(min_delay=0.01,max_delay =10)
    mqttc.connect(mqttbroker,mqttport,keepalive=65535)

    mqttc.loop_forever()

if __name__=='__main__':
    time.sleep(5)
    # connect to sensor
    pEthernetScanner = connect_to_sensor(os.environ.get("WENGLOR_IP","192.168.100.250"),os.environ.get("WENGLOR_PORT", "32001"), 0)
    init_wenglor(pEthernetScanner)
    try:
    # connect to kafka
        _producer=KafkaProducer(bootstrap_servers=os.environ.get('KAFKA_BROKER','127.0.0.1:9092'), 
                                client_id='wenglor_to_kafka_producer', 
                                value_serializer=lambda m:json.dumps(m).encode('utf-8'))
    except NoBrokersAvailable:
        print("No brokers available. Retrying...")
        time.sleep(5)
    producer = SubscriptionHandler(_producer)

    folder_name = "profileData"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    mqttListening("mosquitto",mqttport)
    #mqttListening(mqttbroker,mqttport)
