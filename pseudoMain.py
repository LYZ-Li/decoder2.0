# import time
# import socket
# import os

# trigger = False

# def wenglor(tcp, trigger):
#     tcp.send(str(trigger).encode('utf-8'))

# def main():
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind(('0.0.0.0', os.environ.get("MQTT_PORT",9999)))
    
#     server.listen(1)
#     print('waiting for connection ...')
#     while True:
#         sock, _ = server.accept()

#         trigger = True
#         wenglor(sock, trigger)
#         print('sent start')
#         time.sleep(5)
#         trigger = False
#         wenglor(sock, trigger)
#         print('sent stop')
#         while True:
#             pass

# import socket
# import time
# def tcp_server(host, port):
#     # 创建TCP/IP套接字
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
#     # 绑定到指定的端口
#     server_socket.bind((host, port))
    
#     # 开始监听传入的连接
#     server_socket.listen(5)
    
#     print(f"Listening for connections on {host}:{port}")
    
#     while True:
#         # 等待客户端连接
#         client_socket, client_address = server_socket.accept()
        
#         try:
#             print(f"Connection from {client_address}")
            
#             # 发送响应
#             response = "True"
#             client_socket.sendall(response.encode('utf-8'))
#             print('sent True')
#             time.sleep(5000)
#             response = "False"
#             client_socket.sendall(response.encode('utf-8'))
#             print('sent False')
#             time.sleep(5)

#         finally:
#             # 关闭连接
#             client_socket.close()

# if __name__ == "__main__":
#     HOST = '0.0.0.0'  # 监听所有网络接口
#     PORT = 9999       # 监听的端口号
#     tcp_server(HOST, PORT)

import socket

def tcp_server(host, port):
    # 创建TCP/IP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 绑定到指定的端口
    server_socket.bind((host, port))
    
    # 开始监听传入的连接
    server_socket.listen(5)
    
    print(f"Listening for connections on {host}:{port}")
    
    while True:
        # 等待客户端连接
        client_socket, client_address = server_socket.accept()
        
        try:
            print(f"Connection from {client_address}")
            
            while True:

                # 从键盘获取消息
                message = input("Enter your message: ")
                
                # 发送响应
                client_socket.sendall(message.encode('utf-8'))
                print('message sent!!')

        finally:
            # 关闭连接
            client_socket.close()

if __name__ == "__main__":
    HOST = '0.0.0.0'  # 监听所有网络接口
    PORT = 9999       # 监听的端口号
    tcp_server(HOST, PORT)
