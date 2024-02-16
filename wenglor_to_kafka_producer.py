import ctypes
#import asyncio
from kafka.producer import KafkaProducer
import os, json, pytz
import time
from datetime import datetime
import threading
import queue
import socket

##################################_____________C++ interface_______________##############################

# Load the shared library
#lib = ctypes.CDLL("/app/EthernetScanner/libEthernetScanner.so")  # Replace "your_library_name.so" with the actual name of your library
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
        if handle is not None:
            print("Sensor connected successfully. Handle:", handle)
            return handle
        else:
            raise Exception("Connection failed.")
    except Exception as e:
        print("Connection failed. Error:", e)
        return None

# def initial sensor
def init_wenglor(pScanner):
    write_to_wenglor(pScanner,b'SetAcquisitionStop')
    time.sleep(1)
    write_to_wenglor(pScanner,b'SetAcquisitionLineTime=10000')# set frequency to 100Hz, on Instruction Page 115
    write_to_wenglor(pScanner,b'SetHeartBeat=x=1000')# set heartbeat 1000ms, on Instruction Page 120

# def connect to pseudo master
def connect_to_master():
    master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master.connect((os.environ.get("pseudo_main_ADDRESS",'127.0.0.1'), os.environ.get("pseudo_main_PORT",9999)))
    return master


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
            Queue.put([pdoX, pdoZ, piIntensity, piSignalWidth])
            saveData(savePath,pdoX, pdoZ, piIntensity, piSignalWidth, )
    
#####################################_____________kafka______________############################
class SubscriptionHandler:
    def __init__(self, producer):
        self.producer=producer

    def pack_send(self, x,z,i,w):
        xval = [value for value in x]
        zval = [value for value in z]
        ival = [value for value in i]
        wval = [value for value in w]
        data = {'x': xval, 'z': zval, 'i': ival, 'w': wval}
        val = json.dumps(data)
        #self.producer.send('wenglor', {'key':int(time.time()*1000), 'value':val})#, 'timestamp':datetime.now(pytz.utc).isoformat()})
        try:
            self.producer.send('wenglor_to_kafka', {'key':int(time.time() * 1000), 'value':val})#, 'timestamp':datetime.now(pytz.utc).isoformat()})
            self.producer.flush()
        except Exception as e:
            print(f"Failed to send message: {e}")
def sendKafka(producer):
    while trigger== 'True':
        if not Queue.empty():
            x,z,i,w = Queue.get()
            producer.pack_send(x,z,i,w)

########################################__________main____________#################################
def main():
    try:
        # connect to master
        master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master.connect((os.environ.get('pseudoMain','127.0.0.1'), os.environ.get("pseudo_main_PORT",9999)))
        print('TCP connected')
        # connect to sensor
        pEthernetScanner = connect_to_sensor(os.environ.get("WENGLOR_IP","192.168.100.250"),os.environ.get("WENGLOR_PORT", "32001"), 0)
        init_wenglor(pEthernetScanner)
        # connect to kafka
        _producer=KafkaProducer(bootstrap_servers=os.environ.get('KAFKA_BROKER','127.0.0.1:9092'), 
                               client_id='wenglor_to_kafka_producer', 
                               value_serializer=lambda m:json.dumps(m).encode('utf-8'))
        producer = SubscriptionHandler(_producer)

        folder_name = "profileData"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        last_trigger = None
        threads=[]
        while True:
            global trigger 
            trigger = master.recv(1024).decode('utf-8')
            print(f'received trigger: {trigger}')
            if last_trigger == trigger:
                continue
            elif last_trigger == None and trigger == 'False':
                last_trigger = trigger
                continue
            else:
                last_trigger = trigger
                
            if trigger== 'True':
                # filename
                current_time = datetime.now().strftime("%Y%m%d%H%M")
                savePath = f"{folder_name}/ScanData{current_time}.txt"

                thread_decoder = threading.Thread(target=decoder,args=(pEthernetScanner, savePath, ))
                thread_sendKafka = threading.Thread(target=sendKafka,args=(producer, ))
                threads = [thread_decoder, thread_sendKafka]
                for thread in threads:
                    thread.start()
            elif trigger == 'False':
                last_trigger == None
                print('Stopping data acquisition...')
                for thread in threads:
                    if thread in locals() and thread.is_alive():
                        thread.join()
                print('Data acquisition stopped.')
                write_to_wenglor(pEthernetScanner,b'SetAcquisitionStop')
    finally:
        if pEthernetScanner!= None:
            write_to_wenglor(pEthernetScanner,b'SetAcquisitionStop')
        lib.EthernetScanner_Disconnect(pEthernetScanner)
        print("disconnected")
if __name__=='__main__':
	main()
