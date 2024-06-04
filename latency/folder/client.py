import os
import socket
import time
import json

HOST = 'localhost'
PORT = 65432
SEND_DIRECTORY = '../../../assets/send/120_1K_Full'
LOG_FILE = '../../../assets/log/CLIENT_120_1K_Full.json'

def send_image(image_path, conn, log):
    image_name = os.path.basename(image_path)
    image_name_len = len(image_name).to_bytes(4, 'big')
    with open(image_path, 'rb') as f:
        image_data = f.read()
    image_size = len(image_data).to_bytes(8, 'big')

    start_time = time.time()
    conn.sendall(image_name_len)
    conn.sendall(image_name.encode())
    conn.sendall(image_size)
    conn.sendall(image_data)
    end_time = time.time()

    log.append({
        'image': image_name,
        'start_time': start_time,
        'end_time': end_time
    })

def start_client(image_dir, host='localhost', port=65432):
    log = []

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            image_names = sorted(os.listdir(image_dir))
            for image_name in image_names:
                image_path = os.path.join(image_dir, image_name)
                if os.path.isfile(image_path):
                    send_image(image_path, s, log)
                    print(f'Sent {image_name}')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        with open(LOG_FILE, 'w') as f:
            json.dump(log, f, indent=4)
        print(f'Saved log to {LOG_FILE}')

if __name__ == '__main__':
    start_client(SEND_DIRECTORY, HOST, PORT)
