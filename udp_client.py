import os
import socket

def main():
    # Set up the server's IP address and port number
    UDP_IP = "192.168.0.210"
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
        sequence_number = 0
        data = f.read(1024)
        while data:
            packet = str(sequence_number).zfill(4).encode() + data
            sock.sendto(packet, (UDP_IP, UDP_PORT))
            print(f"Sent packet {sequence_number}")
            sequence_number += 1

            # Wait for an acknowledgement from the server
            ack_received = False
            while not ack_received:
                data, addr = sock.recvfrom(1024)
                if data.decode() == "ACK":
                    ack_received = True

            data = f.read(1024)

    sock.close()
    print("Image sent successfully")

if __name__ == "__main__":
    main()
