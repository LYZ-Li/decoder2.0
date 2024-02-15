import ctypes
import asyncio
from kafka.producer import KafkaProducer
import os, json, pytz
import time
from datetime import datetime



# Load the shared library
lib = ctypes.CDLL("EthernetScanner/libEthernetScanner.so")  # Replace "your_library_name.so" with the actual name of your library

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

async def saveData(savePath,x,z,i,w):
    timestamp_ms = int(time.time() * 1000)

    with open(savePath, "a") as file:
        file.write(f"{timestamp_ms}\n")
        for x_val, z_val, i_val, w_val in zip(x, z, i, w):
            file.write(f"{x_val:.4f},{z_val:.4f},{i_val}\n")#,{w_val}\n")

def send_to_wenglor(pEthernetScanner, ascii_command):
    
    command = ascii_command.encode('utf-8')  # Convert ASCII command to bytes
    command_length = len(command)
    result = lib.EthernetScanner_WriteData(pEthernetScanner, command, command_length)

    # Check the result
    if result == command_length:
        return True  # Invalid handle
    else:
        return False  # Command sent successfully

async def main():
    # initial pEthernetScanner
    pEthernetScanner = None

    # connect to sensor
    pEthernetScanner = connect_to_sensor(os.environ.get("WENGLOR_IP","192.168.100.250"),os.environ.get("WENGLOR_PORT", "32001"), 0)
    try:
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

        # c_double_array_X = (ctypes.c_double * len(pdoX))(*pdoX)
        # c_double_array_Z = (ctypes.c_double * len(pdoZ))(*pdoZ)
        # c_int_array_I = (ctypes.c_int * len(piIntensity))(*piIntensity)
        # c_int_array_W = (ctypes.c_int * len(piSignalWidth))(*piSignalWidth)
        

        folder_name = "profileData"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # 生成文件名
        current_time = datetime.now().strftime("%Y%m%d%H%M")
        savePath = f"{folder_name}/ScanData{current_time}.txt"

        while True:
            result = lib.EthernetScanner_GetXZIExtended(
                pEthernetScanner, pdoX, pdoZ, piIntensity, piSignalWidth,
                #pEthernetScanner, ctypes.POINTER(pdoX),ctypes.POINTER(pdoZ),ctypes.POINTER(piIntensity),ctypes.POINTER(piSignalWidth),
                #pEthernetScanner, c_double_array_X, c_double_array_Z, c_int_array_I, c_int_array_W,
                iBuffer, puiEncoder, pucUSRIO, dwTimeOut, ucBufferRaw, iBufferRaw, iPicCnt
            )
            if result == -1:
                continue
            elif result > 0:
                await saveData(savePath,pdoX,pdoZ,piIntensity,piSignalWidth)

    finally:
        lib.EthernetScanner_Disconnect(pEthernetScanner)
        print("disconnected")
if __name__=='__main__':
	asyncio.run(main())
