import os
import socket

HOST = 'localhost'
PORT = 65432
SEND_DIRECTORY = '../../../assets/send/120_1K_Full'

def send_image(image_path, conn):
    image_name = os.path.basename(image_path)
    image_name_len = len(image_name).to_bytes(4, 'big')
    with open(image_path, 'rb') as f:
        image_data = f.read()
    image_size = len(image_data).to_bytes(8, 'big')

    conn.sendall(image_name_len)
    conn.sendall(image_name.encode())
    conn.sendall(image_size)
    conn.sendall(image_data)

def start_client(image_dir, host='localhost', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        for image_name in os.listdir(image_dir):
            image_path = os.path.join(image_dir, image_name)
            if os.path.isfile(image_path):
                send_image(image_path, s)
                print(f'Sent {image_name}')

if __name__ == '__main__':
    start_client(SEND_DIRECTORY, HOST, PORT)
