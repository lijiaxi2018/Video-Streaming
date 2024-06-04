import os
import socket
import time
import json
import struct

HOST = 'localhost'
PORT = 65432
SEND_DIRECTORY = '../../../assets/send/120_1K_Full'
LOG_FILE = '../../../assets/log/CLIENT_120_1K_Full.json'
BANDWIDTH_THRESHOLD = 700_000_000  # 1MB/s in bytes per second
SLEEP_INTERVAL = 5  # Time to wait in sleep mode before checking bandwidth again (in seconds)

def send_image(image_path, conn, log):
    print(f"Sending image: {image_path}")
    image_name = os.path.basename(image_path)
    image_name_len = len(image_name).to_bytes(4, 'big')
    with open(image_path, 'rb') as f:
        image_data = f.read()
    image_size = len(image_data).to_bytes(8, 'big')

    start_time = time.time()
    conn.sendall(b'IMAGE'.ljust(16, b'\0'))  # Send header indicating an image transfer
    conn.sendall(image_name_len)
    conn.sendall(image_name.encode())
    conn.sendall(image_size)
    conn.sendall(image_data)
    end_time = time.time()

    # Receive server's timestamps
    server_start_time = struct.unpack('d', conn.recv(8))[0]
    server_end_time = struct.unpack('d', conn.recv(8))[0]

    # Calculate bandwidth
    duration = server_end_time - server_start_time
    bandwidth_bps = (len(image_data) * 8) / duration  # bits per second

    log.append({
        'image': image_name,
        'client_start_time': start_time,
        'client_end_time': end_time,
        'server_start_time': server_start_time,
        'server_end_time': server_end_time,
        'duration': duration,
        'bandwidth_bps': bandwidth_bps
    })

    print(f"Sent image: {image_path}, Bandwidth: {bandwidth_bps:.2f} bps")

    return bandwidth_bps

def check_bandwidth(conn):
    print("Checking bandwidth...")
    conn.sendall(b'CHECK_BANDWIDTH'.ljust(16, b'\0'))  # Send header indicating a bandwidth check

    dummy_data = b'\x00' * 1024  # 1KB dummy data
    dummy_size = len(dummy_data).to_bytes(8, 'big')

    start_time = time.time()
    conn.sendall(dummy_size)
    conn.sendall(dummy_data)
    server_start_time = struct.unpack('d', conn.recv(8))[0]
    server_end_time = struct.unpack('d', conn.recv(8))[0]

    duration = server_end_time - server_start_time
    bandwidth_bps = (len(dummy_data) * 8) / duration  # bits per second

    print(f"Checked bandwidth: {bandwidth_bps:.2f} bps")

    return bandwidth_bps

def start_client(image_dir, host='localhost', port=65432):
    log = []
    mode = "normal"  # Start in normal mode

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print("Connected to server")

            image_names = sorted(os.listdir(image_dir))
            image_index = 0

            while image_index < len(image_names):
                image_name = image_names[image_index]
                image_path = os.path.join(image_dir, image_name)
                if os.path.isfile(image_path):
                    if mode == "normal":
                        bandwidth_bps = send_image(image_path, s, log)
                        print(f'Sent {image_name}, Bandwidth: {bandwidth_bps:.2f} bps')

                        if bandwidth_bps < BANDWIDTH_THRESHOLD * 8:  # Convert threshold to bps
                            mode = "sleep"
                            print(f'Bandwidth below threshold. Entering sleep mode...')
                        else:
                            image_index += 1
                    elif mode == "sleep":
                        bandwidth_bps = check_bandwidth(s)
                        print(f'Checking bandwidth in sleep mode: {bandwidth_bps:.2f} bps')

                        if bandwidth_bps >= BANDWIDTH_THRESHOLD * 8:  # Convert threshold to bps
                            mode = "normal"
                            print(f'Bandwidth above threshold. Resuming normal mode...')
                        else:
                            time.sleep(SLEEP_INTERVAL)
    except Exception as e:
        print(f'Error: {e}')
    finally:
        with open(LOG_FILE, 'w') as f:
            json.dump(log, f, indent=4)
        print(f'Saved log to {LOG_FILE}')

if __name__ == '__main__':
    start_client(SEND_DIRECTORY, HOST, PORT)