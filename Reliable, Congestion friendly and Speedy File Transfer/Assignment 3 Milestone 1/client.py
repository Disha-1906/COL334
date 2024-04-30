from socket import *
import hashlib
import threading
import time
import logging

logging.basicConfig(filename='client_log.txt', level=logging.INFO, format='%(message)s')
start_time = time.time()*1000
serverName = '127.0.0.1'
serverPort = 9801
clientSocket = socket(AF_INET, SOCK_DGRAM)
request1 = 'SendSize\n\n'
offset = 0
numByt = 1448
data = []
pending_packets = set()
TIMEOUT = 5

def send_packets():
    # rempak = totalpackets
    global rempak
    while rempak > 0:
        for x in list(pending_packets):
            if data[x] != '':
                continue

            if x == totalpackets-1:
                request = 'Offset: '+ str(1448*x) + '\nNumBytes: ' + str(last_pack) + '\n\n'
            else:
                request = 'Offset: '+ str(1448*x) + '\nNumBytes: ' + str(numByt) + '\n\n'

            clientSocket.sendto(request.encode(), (serverName, serverPort))
            timestamp = time.time() * 1000 - start_time # Current time in milliseconds
            logging.info(f"RequestSent, Offset: {1448*x}, Time: {timestamp}")
            time.sleep(0.0001)
            # print("req sent for offset ", 1448*x)

def receive_packets():
    # rempak = totalpackets
    global rempak
    while rempak > 0:
        try:
            response, serverAddress = clientSocket.recvfrom(2048)
            timestamp = time.time() * 1000 - start_time  # Current time in milliseconds
    
            dec_res = response.decode()
            offset, numBytes, waste, pdata = dec_res.split('\n', 3)
            if waste=="Squished":
                pdata = pdata.split("\n",1)[1]
            is_squished = "Yes" if "Squished" in waste else "No"
            # print("bytes recv -------------------- offset: " + str(offset) + " numBytes: "+ str(numBytes))
            offset_value = int(offset.split(' ')[1])
            logging.info(f"ReplyReceived, Offset: {offset_value}, Time: {timestamp}, Squished: {is_squished}")
            if(data[offset_value//1448]==''):
                data[offset_value//1448] = pdata
                rempak -= 1
                pending_packets.remove(offset_value//1448)
        except Exception as e:
            # Handle other exceptions here if needed
            pass

# print("before sending")
# clientSocket.sendto(request1.encode(), (serverName, serverPort))
# print("after sending")
# response1, serverAddress = clientSocket.recvfrom(2048)
# print(response1.decode())
# totalSize = int(response1.decode().split(' ')[1])
# print(totalSize)

# print("before sending")

while True:
    try:
        clientSocket.sendto(request1.encode(), (serverName, serverPort))
        clientSocket.settimeout(TIMEOUT)
        response1, serverAddress = clientSocket.recvfrom(2048)
        break
    except timeout:
        print("No response received, resending the request...")

# print("after sending")
# print(response1.decode())
totalSize = int(response1.decode().split(' ')[1])
# print(totalSize)


totalpackets = 0  
last_pack = 0
if totalSize % 1448 == 0:
    totalpackets = totalSize // 1448
else:
    totalpackets = totalSize // 1448 + 1
    last_pack = totalSize % 1448
pending_packets = set(range(totalpackets))
global rempak 
rempak = totalpackets
data = ['']*totalpackets

send_thread = threading.Thread(target=send_packets)
recv_thread = threading.Thread(target=receive_packets)

send_thread.start()
recv_thread.start()

send_thread.join()
recv_thread.join()

# Rest of the code remains same...
# with open('output.txt', 'w') as file: 
#     for d in data:
#         file.write(d)

combined_data = ''
for i in data:
    combined_data += i
# print("----------------------------------------------------------------------------------------------------------------------")
# print(combined_data)
# print("-----------------------------------------------------------------------------------------------------------------------")
m = hashlib.md5()
m.update(combined_data.encode())
md5_hash = m.hexdigest()
# print(md5_hash)
request3 = "Submit: 2021CS10578@col334\nMD5: "+str(md5_hash)+"\n\n"
clientSocket.sendto(request3.encode(),(serverName,serverPort))
submit_response,serverAddress = clientSocket.recvfrom(2048)
while submit_response.decode().split(":",2)[0] != "Result":
    submit_response,serverAddress = clientSocket.recvfrom(2048)
res = submit_response.decode()
print(res)    