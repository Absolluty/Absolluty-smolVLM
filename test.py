import cv2
import base64
import requests
import os
from ultralytics import YOLO

# === CONFIGURACIÓN ===
VIDEO_PATH = "input/video_reid01.mp4"  # Cambia esto si tu video está en otro lugar
FRAME_INTERVAL = 30
YOLO_MODEL = "yolov8n.pt"  # Usá un modelo más grande si querés mejor precisión
SERVER_URL = "http://localhost:8080/v1/chat/completions"
PROMPT = """
Respond using only the exact format below — no full sentences, no extra words, no explanation, just these lines, even if some values are unknown:

hair:  
shirt:  
pants:  
skin color:  
estimated gender:  
estimated age:  
estimated height:  

Leave any field blank if not visible or unclear, but always include the field name. Do not write anything else.
"""

# === ENVIAR AL MODELO ===
def query_llama(image_path, prompt):
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "model": "smolvlm",
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": prompt.strip()},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
            ]}
        ],
        "max_tokens": 200,
        "temperature": 0
    }

    response = requests.post(SERVER_URL, json=payload)
    return response.json()["choices"][0]["message"]["content"]

# === PROCESAR VIDEO ===
def process_video():
    os.makedirs("temp_frames", exist_ok=True)
    model = YOLO(YOLO_MODEL)
    cap = cv2.VideoCapture(VIDEO_PATH)
    frame_count = 0
    results_txt = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % FRAME_INTERVAL == 0:
            detections = model(frame)
            for idx, box in enumerate(detections[0].boxes.xyxy):
                cls = int(detections[0].boxes.cls[idx])
                if cls != 0:
                    continue  # Solo personas

                x1, y1, x2, y2 = map(int, box)
                person_crop = frame[y1:y2, x1:x2]
                crop_path = f"temp_frames/frame{frame_count}_person{idx}.jpg"
                cv2.imwrite(crop_path, person_crop)

                try:
                    description = query_llama(crop_path, PROMPT)
                    print(f"\nFrame {frame_count} - Person {idx}:\n{description}")
                    results_txt.append(f"Frame {frame_count} - Person {idx}:\n{description}\n")
                except Exception as e:
                    print(f"Error on frame {frame_count}, person {idx}: {e}")

        frame_count += 1

    cap.release()

    # Guardar resultados
    with open("descriptions_by_person.txt", "w") as f:
        f.writelines(results_txt)

if __name__ == "__main__":
    process_video()
