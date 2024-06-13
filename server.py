import socket


def initialize_server(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(10)
    print(f"server listening on {ip}:{port}!")

    return server

def start_server(server):
    client, address = server.accept()
    print(f"connection from {address}")

    handle_client(server, client, address)

def handle_client(server, client, address):
    while True :
        receive_cmd(server, client)
        #msg = get_user_request()
        #rsp = get_response(msg)
        #send_message(client, rsp)

def receive_cmd(server, client):
    msg = str(input("Enter command: "))
    if msg == "/exit":
        client.close()
        server.close()
        exit()
    send_message(client, msg)

def send_message(client, msg):
    client.sendall(msg.encode())
    print(f"<{msg}> message sent")

def get_user_request():
    return str(input("Enter command: "))


if __name__ == "__main__":
    server = initialize_server("127.0.0.1", 6666)
    start_server(server)