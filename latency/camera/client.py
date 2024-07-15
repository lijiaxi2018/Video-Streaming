import os
import socket
import time
import json
import cv2

HOST = 'localhost'
PORT = 65432
LOG_FILE = './temp/client.json'
CAMERA_SOURCE = 0
WIDTH = 1920 / 4
HEIGHT = 1080 / 4

def send_image(frame, frame_count, conn, log):
    image_name = f'frame_{frame_count}.jpg'
    image_name_len = len(image_name).to_bytes(4, 'big')
    _, image_data = cv2.imencode('.jpg', frame)
    image_data = image_data.tobytes()
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

def start_client(host='localhost', port=65432, width=640, height=480):
    log = []

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            cap = cv2.VideoCapture(CAMERA_SOURCE)  # 0 is usually the default camera
            if not cap.isOpened():
                print("Error: Could not open camera.")
                return
            
            # Set the resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                send_image(frame, frame_count, s, log)
                print(f'Sent frame_{frame_count}.jpg')
                frame_count += 1

                # Wait a bit before capturing the next frame
                time.sleep(1)

            cap.release()

    except Exception as e:
        print(f'Error: {e}')
    finally:
        LOG_DIR = os.path.dirname(LOG_FILE)
        os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the directory exists
        with open(LOG_FILE, 'w') as f:
            json.dump(log, f, indent=4)
        print(f'Saved log to {LOG_FILE}')

if __name__ == '__main__':
    start_client(HOST, PORT, width=WIDTH, height=HEIGHT)  # Example: setting resolution to 1280x720
