import tkinter as tk
from tkinter import messagebox
import cv2
import os
import numpy as np

# ✅ Load Face Recognition Model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
recognizer = cv2.face.LBPHFaceRecognizer_create()

if os.path.exists("trained_model.yml"):
    recognizer.read("trained_model.yml")

# ✅ Function to open Dataset Management Page
def open_dataset_management():
    dataset_window = tk.Tk()
    dataset_window.title("Dataset Management")
    dataset_window.geometry("600x500")
    dataset_window.config(background="lightgray")

    # ✅ Entries and Labels
    tk.Label(dataset_window, text="Name:", font=("Helvetica", 14)).pack(pady=5)
    name_entry = tk.Entry(dataset_window, width=40)
    name_entry.pack()

    tk.Label(dataset_window, text="Age:", font=("Helvetica", 14)).pack(pady=5)
    age_entry = tk.Entry(dataset_window, width=40)
    age_entry.pack()

    tk.Label(dataset_window, text="ID:", font=("Helvetica", 14)).pack(pady=5)
    id_entry = tk.Entry(dataset_window, width=40)
    id_entry.pack()

    progress_label = tk.Label(dataset_window, text="Captured 0/5 images", font=("Helvetica", 12))
    progress_label.pack(pady=5)

    # ✅ Function to capture face images
    def capture_image():
        cap = cv2.VideoCapture(0)
        count = 0
        os.makedirs("dataset", exist_ok=True)

        while count < 5:
            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Error", "Failed to capture image!")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face_img = gray[y:y+h, x:x+w]
                cv2.imwrite(f"dataset/{id_entry.get()}_{count}.jpg", face_img)
                count += 1
                progress_label.config(text=f"Captured {count}/5 images")
                if count >= 5:
                    break

            cv2.imshow("Capturing Faces", frame)
            cv2.waitKey(100)

        cap.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Success", "Face images captured successfully!")

    # ✅ Function to save user data (placeholder)
    def save_to_database():
        user_data = {
            "Name": name_entry.get(),
            "Age": age_entry.get(),
            "ID": id_entry.get()
        }
        print("Saved:", user_data)  # You can later save this to SQLite or CSV
        messagebox.showinfo("Success", "Data saved successfully!")

    tk.Button(dataset_window, text="Capture Image", font=("Helvetica", 14), command=capture_image).pack(pady=5)
    tk.Button(dataset_window, text="Save to Database", font=("Helvetica", 14), command=save_to_database).pack(pady=5)

    dataset_window.mainloop()

# ✅ Function for Face Login
def face_login():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

        for (x, y, w, h) in faces:
            face_roi = gray[y:y + h, x:x + w]
            label, confidence = recognizer.predict(face_roi)

            if confidence < 60:
                cap.release()
                cv2.destroyAllWindows()
                messagebox.showinfo("Success", "Face recognized! Login successful.")
                open_dataset_management()
                return
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow("Face Login", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    messagebox.showerror("Error", "Face not recognized!")

# ✅ Main Window
window = tk.Tk()
window.title("Login")
window.geometry("600x400")
window.config(background="lightgrey")

tk.Button(window, text="Login with Face", font=("Helvetica", 14), command=face_login).pack(pady=20)

window.mainloop()
