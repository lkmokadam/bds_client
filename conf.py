'''import netifaces

interfaces =  netifaces.interfaces()
ip_list = []
for interface in interfaces:
    addrs = netifaces.ifaddresses(interface)
    if netifaces.ifaddresses(interface).get(2):
        ip_list.append(netifaces.ifaddresses(interface).get(2)[0].get('addr'))
print ip_list


import socket
for ip in ip_list:
    if str(ip).startswith("11.24."):
        print ip

MACHINE_IP = ip
SERVER_IP = ip

CAMERA_PORT = 5001
TEST_MACHINE_PORT = 5002
SERVER_PORT = 5003'''

'''CAMERA_IP_PORT = "tcp://localhost:5001"
CAMERA_FOR_SERVER_PORT = "tcp://*:5001"
TEST_MACHINE_IP_PORT = "tcp://localhost:5002"
SERVER_IP_PORT = "tcp://localhost:5003"
SERVER_FOR_SERVER_PORT = "tcp://*:5003"'''