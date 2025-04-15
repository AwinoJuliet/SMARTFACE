import cv2
import os
import numpy as np
from PIL import Image
import tkinter as tk

# Initialize face recognizer and Haar Cascade
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Automatically crop and resize face from frame
def crop_and_resize_face(gray, x, y, w, h, size=(200, 200)):
    face = gray[y:y + h, x:x + w]
    return cv2.resize(face, size)

# Train model from dataset folder
def train_model(data_dir='dataset'):
    faces = []
    labels = []
    label_dict = {}
    current_label = 0

    for file in os.listdir(data_dir):
        if file.endswith(".jpg"):
            path = os.path.join(data_dir, file)
            img = Image.open(path).convert('L')
            img_np = np.array(img, 'uint8')
            name = "_".join(file.split("_")[:-1])
            if name not in label_dict:
                label_dict[name] = current_label
                current_label += 1
            faces.append(cv2.resize(img_np, (200, 200)))
            labels.append(label_dict[name])

    if faces:
        recognizer.train(faces, np.array(labels))
        return label_dict
    return {}

# GUI Welcome Access Screen
def show_welcome_screen(name):
    win = tk.Tk()
    win.title("Access Granted")
    win.geometry("300x200")
    win.configure(bg="green")

    tk.Label(win, text="✅", font=("Arial", 50), bg="green", fg="white").pack(pady=10)
    tk.Label(win, text=f"Welcome, {name.replace('_', ' ')}", font=("Arial", 16), bg="green", fg="white").pack()
    win.after(3000, win.destroy)
    win.mainloop()

# GUI Denied Access Screen
def show_denied_screen():
    win = tk.Tk()
    win.title("Access Denied")
    win.geometry("300x200")
    win.configure(bg="red")

    tk.Label(win, text="❌", font=("Arial", 50), bg="red", fg="white").pack(pady=10)
    tk.Label(win, text="Access Denied", font=("Arial", 16), bg="red", fg="white").pack()
    win.after(3000, win.destroy)
    win.mainloop()

# Run Face Recognition
def recognize_faces(label_dict):
    reverse_labels = {v: k for k, v in label_dict.items()}
    cap = cv2.VideoCapture(0)
    recognized = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        for (x, y, w, h) in faces:
            face = crop_and_resize_face(gray, x, y, w, h)
            id_, confidence = recognizer.predict(face)

            if id_ in reverse_labels and confidence < 45:  # STRONG match
                name = reverse_labels[id_]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Welcome: {name.replace('_', ' ')}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cap.release()
                cv2.destroyAllWindows()
                show_welcome_screen(name)
                recognized = True
                break
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "Access Denied", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Smart Face Recognition Access", frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or recognized:
            break

    cap.release()
    cv2.destroyAllWindows()

    if not recognized:
        show_denied_screen()

# --- MAIN ---
if __name__ == "__main__":
    labels = train_model('dataset')
    if labels:
        recognize_faces(labels)
    else:
        print("❌ No training data found. Add images to the dataset folder.")
