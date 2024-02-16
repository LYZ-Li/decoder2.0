import ctypes
import asyncio
from kafka.producer import KafkaProducer
import os, json, pytz
from datetime import datetime
import time


# Load the shared library
lib = ctypes.CDLL("EthernetScanner/libEthernetScanner.so")  # Replace "your_library_name.so" with the actual name of your library

# Define the argument and return types for the function
lib.EthernetScanner_Connect.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.EthernetScanner_Connect.restype = ctypes.c_void_p

lib.EthernetScanner_Disconnect.restype = ctypes.c_void_p
lib.EthernetScanner_Disconnect.argtypes = [ctypes.c_void_p]

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

# def connect to sensor
def connect_to_sensor(ip, port, timeout):
    try:
        chIP = ip.encode("utf-8")
        chPort = port.encode("utf-8")
        handle = lib.EthernetScanner_Connect(chIP, chPort, timeout)
        if handle is not None:
            print("Connection successful. Handle:", handle)
            return handle
        else:
            raise Exception("Connection failed.")
    except Exception as e:
        print("Connection failed. Error:", e)
        return None

class SubscriptionHandler:
    def __init__(self, producer):
        self.producer=producer

    async def sendKafka(self, x,z,i,w):
        xval = [value for value in x]
        zval = [value for value in z]
        ival = [value for value in i]
        wval = [value for value in w]
        data = {'x': xval, 'z': zval, 'i': ival, 'w': wval}
        val = json.dumps(data)
        #self.producer.send('wenglor', {'key':int(time.time()*1000), 'value':val})#, 'timestamp':datetime.now(pytz.utc).isoformat()})
        try:
            self.producer.send('test', {'key':int(time.time() * 1000), 'value':val})#, 'timestamp':datetime.now(pytz.utc).isoformat()})
        except Exception as e:
            print(f"Failed to send message: {e}")


async def main():
    producer=KafkaProducer(bootstrap_servers='127.0.0.1:9092', client_id='wenglor_to_kafka_producer', value_serializer=lambda m:json.dumps(m).encode('utf-8'))
    #producer=KafkaProducer(bootstrap_servers=[os.environ.get('KAFKA_BROKER')], client_id='wenglor_to_kafka_producer', value_serializer=lambda m:json.dumps(m).encode('utf-8'))
    # initial pEthernetScanner
    pEthernetScanner = None

    # connect to sensor
    pEthernetScanner = connect_to_sensor(os.environ.get("WENGLOR_IP","192.168.100.250"),os.environ.get("WENGLOR_PORT", "32001"), 0)
    try:
        handler=SubscriptionHandler(producer)
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

        while True:
            result = lib.EthernetScanner_GetXZIExtended(
                pEthernetScanner, pdoX, pdoZ, piIntensity, piSignalWidth,
                iBuffer, puiEncoder, pucUSRIO, dwTimeOut, ucBufferRaw, iBufferRaw, iPicCnt
            )
            if result == -1:
                continue
            elif result > 0:
                await handler.sendKafka(pdoX,pdoZ,piIntensity,piSignalWidth)

    finally:
        lib.EthernetScanner_Disconnect(pEthernetScanner)
        print("disconnected")
if __name__=='__main__':
	asyncio.run(main())
