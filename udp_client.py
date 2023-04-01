import os
import socket
import sys

def main():
    # Set up the server's IP address and port number
    UDP_IP = "192.168.0.210"
    UDP_PORT = 8080

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Open the image file and get its size
    filename = "test.jpg"
    file_size = os.path.getsize(filename)

    # Calculate the total number of packets
    packet_size = 1024
    total_packets = file_size // packet_size + 1

    # Send the image file size and total number of packets to the server
    sock.sendto(str(file_size).encode(), (UDP_IP, UDP_PORT))
    sock.sendto(str(total_packets).encode(), (UDP_IP, UDP_PORT))
    print(f"File size: {file_size} bytes")
    print(f"Total packets: {total_packets}")

    # Send the image file data to the server
    with open(filename, "rb") as f:
        sequence_number = 1
        data = f.read(packet_size)
        while data:
            packet = str(sequence_number).zfill(4).encode() + data
            sock.sendto(packet, (UDP_IP, UDP_PORT))
            print(f"Sent packet {sequence_number}/{total_packets}")
            sequence_number += 1

            # Wait for an acknowledgement from the server
            ack_received = False
            while not ack_received:
                data, addr = sock.recvfrom(1024)
                if data.decode() == "ACK":
                    ack_received = True
            print(f"Received ACK for packet {sequence_number-1}/{total_packets}")
            data = f.read(packet_size)

    # Close the socket and shut down
    sock.close()
    print("File sent successfully")

    # Exit on the console
    input("Press enter to exit")
    sys.exit()

if __name__ == "__main__":
    main()
