import socket
import os

# Prompt the user to enter the server's IP address
UDP_IP = input("Enter the server's IP address: ")

#Set up the server's port number
UDP_PORT = 8080

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Open the image file and get its size
filename = "test.jpg"
file_size = os.path.getsize(filename)

# Send the image file size to the server
sock.sendto(str(file_size).encode(), (UDP_IP, UDP_PORT))

# Send the image file data to the server
with open(filename, "rb") as f:
    data = f.read(1024)
    while data:
        sock.sendto(data, (UDP_IP, UDP_PORT))
        data = f.read(1024)

sock.close()
print("Image sent successfully")