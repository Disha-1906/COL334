import socket
import threading
import time
global count, tt
count=0
lines_data = [None for i in range(1000)]
connected = False
def connect_to_server():
# ---------------------------------------------UNCOMMENT FOR ERROR HANDLING----------------------------------------------------------------------
    # while count!=1000:
# ---------------------------------------------------------------------------------------------------------------------------------
    try:
        server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(('10.17.51.115', 9801))
        buffer = ""
        server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("created socket")
        server_s.bind(('0.0.0.0',55505))
        server_s.listen(5)
        print("listening for connections")
        client_socket, addr = server_s.accept()
        print(f"Accepted connection from {addr}")
        while count != 1000:
            request = "SENDLINE\n"
            server_socket.send(request.encode())
            data = server_socket.recv(1024)
            try:
                client_socket.send(data)
            except:
                pass
        if count==1000:
            et = time.time()
            print(et-tt)                    
            submission_message = "SUBMIT\ndisha@col334-672\n1000\n"
            server_socket.send(submission_message.encode())
            for i in range(0,1000):
                msg = str(i)+"\n"
                server_socket.send(msg.encode())
                msg2 = lines_data[i]+"\n"
                server_socket.send(msg2.encode())
            res = server_socket.recv(1024).decode().strip()
            et = time.time()
            print(et-tt)
            while(res.startswith("SUBMIT")!=True):
                res = server_socket.recv(1024).decode().strip()
            print(res)
            server_socket.close()
            et = time.time()
            print(et-tt,'seconds')
    except Exception as e:
        print(f"Error in connect_to_server: {e}")
def update_lines_data(line_number, line_content):
    global count
    count+=1
    lines_data[line_number] = line_content
def client_handler(client_address):
    global connected
# ---------------------------------UNCOMMENT FOR ERROR HANDLING--------------------------------------------------------------------
    # while count!=1000:
#---------------------------------------------------------------------------------------------------------------------------------- 
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# --------------------------------UNCOMMENT FOR ERROR HANDLING---------------------------------------------------------------------
            # client_socket.settimeout(40)
# ---------------------------------------------------------------------------------------------------------------------------------
        client_socket.connect(client_address)
        buffer = ""
        connected = True
        while count!=1000:
            message = client_socket.recv(1024).decode()
# -------------------------UNCOMMENT FOR ERROR HANDLING----------------------------------------------------------------------------
                # print("recieved",count)
# ----------------------------------------------------------------------------------------------------------------------------------
            buffer += message
            while buffer.count('\n') >= 2:
                line_number_str, line_content, buffer = buffer.split('\n', 2)
                if(line_number_str.isdigit()):
                    line_number = int(line_number_str)
                    if(lines_data[line_number]==None):
                        update_lines_data(line_number,line_content)
            if count==1000:
                client_socket.send("DONE".encode())
                client_socket.close()
                break
    except Exception as e:
        connected = False
        if client_socket:
            client_socket.close()
        print(f"Error in client_handler ({client_address}): {e}")
def main():
    global tt
    tt = time.time()
    threads = []
    server_thread = threading.Thread(target=connect_to_server)
    threads.append(server_thread)
    server_thread.start()
    print("after start")
    other_clients = [("10.194.3.65",55555)]
    for client_address in other_clients:
        client_thread = threading.Thread(target=client_handler, args=(client_address,))
        threads.append(client_thread)
        client_thread.start()

    for thread in threads:
        thread.join()
    print("All threads completed!")
    et=time.time()
    print(et-tt,'seconds')
if __name__ == "__main__":
    main()
