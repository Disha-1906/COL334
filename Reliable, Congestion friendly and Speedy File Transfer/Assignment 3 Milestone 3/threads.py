import threading
from socket import *
import hashlib
import time
import csv
# squish_timestamps = []
# burst_sizes=[]
# sequence_numbers = []
data_log = []
offset_log = []
begin= time.time()
serverName = '10.17.7.134'
serverPort = 9802
clientSocket = socket(AF_INET, SOCK_DGRAM)
numByt = 1448
request1 = 'SendSize\n\Reset\n\n'
INITIAL_TIMEOUT = 0.05

# Dynamic Timeout parameters
avg_rtt = INITIAL_TIMEOUT  # Initial average RTT (in seconds)
ALPHA = 0.75  # Weight for the EMA
MARGIN = 4 # Margin factor
BETA = 0.25
dev_rtt = 0.0
flag = 0
# AIMD parameters
base_burst_size = 1  # initial size of the burst
burst_size = base_burst_size
alpha = 1  # amount to increase during additive increase
beta = 0.8  # fraction to decrease during multiplicative decrease

data = ['']
#local server ---- flag = 3
def send_burst(offsets):
    global flag
    for offset in offsets:
        if offset == totalpackets-1:
            request = 'Offset: '+ str(1448*offset) + '\nNumBytes: ' + str(last_pack) + '\n\n'
        else:
            request = 'Offset: '+ str(1448*offset) + '\nNumBytes: ' + str(numByt) + '\n\n'
        clientSocket.sendto(request.encode(), (serverName, serverPort))
        print("req sent")
        offset_log.append((time.time()-begin, 1448*offset, 'request'))
        # time.sleep(0.1**20)
        # if(flag==2):
        time.sleep(0.00000000000015)
        #     flag = 0
        # flag += 1
        

totalSize = 0
while True:
    try:
        clientSocket.sendto(request1.encode(), (serverName, serverPort))
        clientSocket.settimeout(avg_rtt + MARGIN * dev_rtt)  # set the timeout based on avg_rtt and margin
        response1, serverAddress = clientSocket.recvfrom(2048)
        totalSize = int(response1.decode().split(' ')[1])
        break
    except timeout:
        print(f"No response received, resending the request... Current Average RTT: {avg_rtt:.3f}s")

totalpackets = totalSize // 1448 + (1 if totalSize % 1448 != 0 else 0)
last_pack = totalSize % 1448
data = [''] * totalpackets
pending_packets = set(range(totalpackets))
received_packets = set(range(totalpackets))

def receive_data():
    while(received_packets):
    # global avg_rtt,dev_rtt,burst_size
    # start_time = time.time()
        try:
            clientSocket.settimeout(INITIAL_TIMEOUT)
            response,_ = clientSocket.recvfrom(2048)
            
            # rtt = time.time() - start_time
            # with lock:
            # avg_rtt = (1 - ALPHA) * avg_rtt + ALPHA * rtt
            # dev_rtt = (1 - BETA) * dev_rtt + BETA * abs(rtt - avg_rtt)
            
            dec_res = response.decode()
            if dec_res.startswith("Offset"):
                offset, numBytes, waste, pdata = dec_res.split('\n', 3)
                if waste == "Squished":
                    pdata = pdata.split("\n", 1)[1]

                offset_value = int(offset.split(' ')[1])
                offset_log.append((time.time() - begin, offset_value, 'reply'))
                print("bytes recv -------------------- offset: " + str(offset) + " numBytes: "+ str(numBytes))
                if data[offset_value // 1448] == '':
                    data[offset_value // 1448] = pdata
                    current_time = time.time() - begin
                    data_log.append((current_time, burst_size, waste == "Squished"))
                    received_packets.remove(offset_value // 1448)
            # burst_size += alpha
            # burst_sizes.append((time.time(), burst_size))
            # print("new burst size is , ",burst_size)

        except timeout:
            # with lock:
            # burst_size = max(base_burst_size, int(burst_size * beta))
            # print("burst size is ",burst_size)
            continue

thread = threading.Thread(target = receive_data)
thread.start()

while pending_packets:
    threads=[]
    # current_burst = list(pending_packets)[:burst_size]
    # time.sleep(0.00000015)
    send_burst(list(pending_packets))
    time.sleep(0.00000001)
    pending_packets=received_packets
    # threads.append(thread)
    # thread.start()
    



thread.join()
    # for t in threads:
    #     t.join()
    # start_time = time.time()
combined_data = ''.join(data)
m = hashlib.md5()
m.update(combined_data.encode())
md5_hash = m.hexdigest()
request3 = "Submit: 2021CS10578@col334\nMD5: "+str(md5_hash)+"\n\n"
while True:
    clientSocket.sendto(request3.encode(), (serverName, serverPort))
    try:
        submit_response, serverAddress = clientSocket.recvfrom(2048)
        while submit_response.decode().split(":", 2)[0] != "Result":
            submit_response, serverAddress = clientSocket.recvfrom(2048)    
        res = submit_response.decode()
        print(res)
        # print(time.time()*1000 - begin)
        break
    except:
        pass

with open("data_log.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Timestamp", "Burst Size", "Squished"])  # Write header
    writer.writerows(data_log)

with open("offset_log.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Timestamp", "Offset", "Type"])  # Write header
    writer.writerows(offset_log)

