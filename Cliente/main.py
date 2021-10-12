import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

msg = "Hi, Im udp client"
sock.sendto(msg.encode("utf-8"), ("127.0.0.1", 12345))
data, addr = sock.recvfrom(4096)
print("Server says:")
print(str(data))
sock.close()
