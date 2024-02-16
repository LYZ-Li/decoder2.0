import time
import socket
import os

trigger = False
def wenglorInit():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server.bind(('0.0.0.0', os.environ.get("MQTT_PORT",9999)))
    
    server.listen(1)
    print('waiting for connection ...')
    while True:
        sock, _ = server.accept()
        return sock

def wenglor(tcp, trigger):
    tcp.send(str(trigger).encode('utf-8'))



def main():
    tcp = wenglorInit()
    trigger = True
    wenglor(tcp, trigger)
    time.sleep(5)
    trigger = False
    wenglor(tcp, trigger)
