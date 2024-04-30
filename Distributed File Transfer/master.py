import socket
import threading
import time

global count, tt, connected, flag
count = 0
connected = True
flag = False

# ---------------------------------------------UNCOMMENT FOR ERROR HANDLING------------------------------------
# global lines_sent
# lines_sent = False
# -------------------------------------------------------------------------------------------------------------

lines_data = [None for i in range(1000)] 
client_thrds = []
connected_clients = set()
mapping={"10.194.26.65":"disha","10.194.36.206":"srushti","10.194.8.238":"namrata","10.194.2.26":"aastha"}

def connect_to_server():
# ------------------------------------------------UNCOMMENT FOR ERROR HANDLING----------------------------------
    # while count!=1000:
# --------------------------------------------------------------------------------------------------------------
        try:
            server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect(('10.17.51.115', 9801))
            buffer = ""
            while count != 1000:
# -----------------------------------------------UNCOMMENT FOR ERROR HANDLING------------------------------------
                # time.sleep(5)
# ---------------------------------------------------------------------------------------------------------------
                request = "SENDLINE\n"
                server_socket.send(request.encode())
                data = server_socket.recv(1024).decode()
                buffer += data
                while buffer.count('\n') >= 2:
                    line_number_str, line_content, buffer = buffer.split('\n', 2)
                    if(line_number_str.isdigit()):
                        line_number = int(line_number_str)
                        if (line_number!=-1) and (lines_data[line_number] == None):
                            update_lines_data(line_number,line_content)
                            if count==1000:
                                break
                if count==1000:
# -----------------------------------------UNCOMMENT FOR ERROR HANDLING-------------------------------------------------------
                # if lines_sent and count==1000:
# ----------------------------------------------------------------------------------------------------------------------------
                    et = time.time()
                    print(et-tt)   
                    for x in client_thrds:
                        x.start()
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
                    break
        except Exception as e:
            print(f"Error in connect_to_server: {e}")

def start_server():
    """Starts the server to listen on the given port."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0',55555))
    server_socket.listen(5)  # Adjust the backlog as needed
    
    print(f"Server started. Listening for connections on port {55555}")

    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        client_thrds.append(client_thread)

# --------------------------------UNCOMMENT FOR ERROR HANDLING-------------------------------------------------
    # while True:
    #     conn, addr = server_socket.accept()
    #     print("Accepted connection from ", conn, addr)
    #     if addr[0] not in connected_clients:
    #         client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
    #         client_thrds.append(client_thread)
    #         connected_clients.add(addr[0])
    #         # thread_map[addr[0]] = client_thread
    #     else:
    #         new_client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
    #         new_client_thread.start()
    #         print("thread started again")
# --------------------------------------------------------------------------------------------------------------

def handle_client_connection(conn:socket, addr):
    global count
    global flag
    global lines_sent
    """Handle individual client connections."""
    while not flag:
# --------------------------------------------------------UNCOMMENT FOR ERROR HANDLING----------------------------
    # while True:
# ----------------------------------------------------------------------------------------------------------------
        print(f"Accepted connection from {addr}")
        try:
            i=0
            while i<1000:
# --------------------------------------------------------UNCOMMENT FOR ERROR HANDLING-----------------------------
                # time.sleep(2)
# -----------------------------------------------------------------------------------------------------------------
                send_message = str(i)+"\n"+lines_data[i]+"\n"
                conn.send(send_message.encode())
                i+=1
            if i==1000:
                lines_sent = True
        except Exception as e:  
            print(f"Error handling client {addr}: {e}")
        finally:
            conn.close()
            flag = True
            

def update_lines_data(line_number, line_content):
    global count
    lines_data[line_number] = line_content
    count += 1
    # print("Count is ", count)


def client_handler(client_address):
    global connected
# --------------------------UNCOMMENT FOR ERROR HANDLING-----------------------------------------------------
    # while count!=1000:
# ------------------------------------------------------------------------------------------------------------
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
# --------------------------UNCOMMENT FOR ERROR HANDLING-----------------------------------------------------
            # client_socket.settimeout(5)
# ------------------------------------------------------------------------------------------------------------
        client_socket.connect(client_address)
        buffer = ""
# --------------------------UNCOMMENT FOR ERROR HANDLING & -----------------------------------------------------
            # connected = True
            # while connected and count!=1000:
# ------------------------------------------------------------------------------------------------------------
        while True:
            message = client_socket.recv(1024).decode()
            # if(len(message)>0):
                # print("recieved from ",mapping[client_address[0]])
            buffer += message
            while buffer.count('\n') >= 2:
                line_number_str, line_content, buffer = buffer.split('\n', 2)
                if(line_number_str.isdigit()):
                    line_number = int(line_number_str)
                    if (line_number!=-1) and (lines_data[line_number] == None):
                        update_lines_data(line_number,line_content)
                        if count==1000:
                            break
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
    other_clients = [("10.194.2.26",55505)]
    for client_address in other_clients:
        client_thread = threading.Thread(target=client_handler, args=(client_address,))  
        threads.append(client_thread)
        client_thread.start()

    listener_thread = threading.Thread(target=start_server)
    threads.append(listener_thread)
    listener_thread.start()
    server_thread = threading.Thread(target=connect_to_server)
    threads.append(server_thread)
    server_thread.start()
    for thread in threads:
        thread.join()
    print("All threads completed!")
    et=time.time()
    print(et-tt,'seconds')

# Start the program
if __name__ == "__main__":
    main()