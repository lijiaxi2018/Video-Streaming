import os
import socket
import time
import json
import struct
from get_power import readAllValue

HOST = 'localhost'
PORT = 65432
RECEIVE_DIRECTORY = '../../../assets/receive/120_1K_Full'
LOG_FILE = '../../../assets/log/SERVER_120_1K_Full.json'

def save_image(image_data, save_path):
    with open(save_path, 'wb') as f:
        f.write(image_data)

def recv_all(conn, num_bytes):
    data = b''
    while len(data) < num_bytes:
        packet = conn.recv(num_bytes - len(data))
        if not packet:
            return None
        data += packet
    return data

def start_server(result_dir, host='localhost', port=65432):
    log = []

    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            print(f'Server listening on {host}:{port}...')

            conn, addr = s.accept()
            with conn:
                print(f'Connected by {addr}')
                while True:
                    image_name_len_data = recv_all(conn, 4)
                    if not image_name_len_data:
                        break
                    image_name_len = int.from_bytes(image_name_len_data, 'big')

                    image_name = recv_all(conn, image_name_len).decode()
                    image_size_data = recv_all(conn, 8)
                    image_size = int.from_bytes(image_size_data, 'big')

                    start_time = time.time()
                    image_data = recv_all(conn, image_size)
                    end_time = time.time()

                    save_path = os.path.join(result_dir, image_name)
                    save_image(image_data, save_path)
                    print(f'Saved {image_name} to {save_path}')

                    log.append({
                        'image': image_name,
                        'start_time': start_time,
                        'end_time': end_time,
                        'energy': readAllValue(),
                    })

                    # Send server's timestamps back to client
                    conn.sendall(struct.pack('d', start_time))
                    conn.sendall(struct.pack('d', end_time))
    except Exception as e:
        print(f'Error: {e}')
    finally:
        with open(LOG_FILE, 'w') as f:
            json.dump(log, f, indent=4)
        print(f'Saved log to {LOG_FILE}')

if __name__ == '__main__':
    start_server(RECEIVE_DIRECTORY, HOST, PORT)