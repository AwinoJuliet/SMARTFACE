import os
import cv2
import sqlite3
import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
from PIL import Image, ImageTk
import numpy as np
import bcrypt
import pyttsx3

# -------------------------
# Setup
# -------------------------
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
recognizer = cv2.face.LBPHFaceRecognizer_create()

if not os.path.exists("dataset"):
    os.makedirs("dataset")

# -------------------------
# DB Setup
# -------------------------
def connect_db():
    conn = sqlite3.connect("face_recognition.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        regno TEXT,
        year TEXT
    )''')
    conn.commit()
    return conn

# -------------------------
# Face Cropping + Resizing
# -------------------------
def crop_and_resize_face(gray, x, y, w, h):
    face = gray[y:y+h, x:x+w]
    resized = cv2.resize(face, (200, 200))
    return resized

# -------------------------
# Capture Faces
# -------------------------
def capture_faces(name):
    cap = cv2.VideoCapture(0)
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = crop_and_resize_face(gray, x, y, w, h)
            count += 1
            cv2.imwrite(f"dataset/{name}_{count}.jpg", face)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Capturing Faces - Q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 20:
            break

    cap.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Done", f"Captured {count} images for {name}")

# -------------------------
# Train Model
# -------------------------
def train_model():
    faces, labels = [], []
    label_map, label_id = {}, 0

    for file in os.listdir("dataset"):
        if file.endswith(".jpg"):
            path = os.path.join("dataset", file)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            name = "_".join(file.split("_")[:-1])
            if name not in label_map:
                label_map[name] = label_id
                label_id += 1
            faces.append(img)
            labels.append(label_map[name])

    if faces:
        recognizer.train(faces, np.array(labels))
        recognizer.save("trainer.yml")
        messagebox.showinfo("Training", "Training completed.")
    else:
        messagebox.showwarning("Warning", "No data to train.")

# -------------------------
# Recognize Face
# -------------------------
def recognize_faces():
    if not os.path.exists("trainer.yml"):
        messagebox.showerror("Error", "Train the model first.")
        return

    recognizer.read("trainer.yml")
    cap = cv2.VideoCapture(0)

    label_map = {}
    i = 0
    for file in os.listdir("dataset"):
        if file.endswith(".jpg"):
            name = "_".join(file.split("_")[:-1])
            if name not in label_map.values():
                label_map[i] = name
                i += 1

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = crop_and_resize_face(gray, x, y, w, h)
            id_, conf = recognizer.predict(face)
            if conf < 60:
                name = label_map.get(id_, "Unknown")
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
                cv2.putText(frame, f"{name}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                speak(f"Access granted. Welcome {name}")
                show_access_granted(name)
                cap.release()
                cv2.destroyAllWindows()
                return
            else:
                cv2.putText(frame, "Unknown", (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# -------------------------
# Voice Greeting
# -------------------------
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# -------------------------
# Show Access Granted
# -------------------------
def show_access_granted(name):
    win = Toplevel()
    win.title("Access Granted")
    win.geometry("300x250")
    win.config(bg="green")

    tk.Label(win, text="✅ ACCESS GRANTED", font=("Arial", 16, "bold"), fg="white", bg="green").pack(pady=10)
    tk.Label(win, text=f"Welcome, {name.replace('_', ' ')}", font=("Arial", 12), bg="green", fg="white").pack(pady=5)

    tick_img = Image.open("tick.png").resize((100, 100))
    tick_photo = ImageTk.PhotoImage(tick_img)
    label = tk.Label(win, image=tick_photo, bg="green")
    label.image = tick_photo
    label.pack()

    tk.Button(win, text="Close", command=win.destroy).pack(pady=10)

# -------------------------
# Register Student
# -------------------------
def user_details_form():
    form = Toplevel()
    form.title("Register Student")
    form.geometry("300x300")

    tk.Label(form, text="Full Name").pack()
    name_entry = tk.Entry(form)
    name_entry.pack()

    tk.Label(form, text="Reg No").pack()
    reg_entry = tk.Entry(form)
    reg_entry.pack()

    tk.Label(form, text="Year").pack()
    year_entry = tk.Entry(form)
    year_entry.pack()

    def save_user():
        name = name_entry.get().strip()
        reg = reg_entry.get().strip()
        year = year_entry.get().strip()
        if not all([name, reg, year]):
            messagebox.showwarning("Missing", "All fields required.")
            return
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, regno, year) VALUES (?, ?, ?)", (name, reg, year))
        conn.commit()
        conn.close()
        capture_faces(name.replace(" ", "_"))
        train_model()
        form.destroy()

    tk.Button(form, text="Register", command=save_user).pack(pady=20)
    tk.Button(form, text="Back", command=form.destroy).pack()

# -------------------------
# Admin Dashboard
# -------------------------
def open_dashboard():
    dash = Toplevel()
    dash.title("Admin Dashboard")
    dash.geometry("300x300")

    ttk.Button(dash, text="Register Student", command=user_details_form).pack(pady=10)
    ttk.Button(dash, text="Face Detect", command=recognize_faces).pack(pady=10)
    ttk.Button(dash, text="Train Model", command=train_model).pack(pady=10)
    ttk.Button(dash, text="Exit", command=dash.destroy).pack(pady=10)

# -------------------------
# Auth Screens
# -------------------------
def login_screen():
    win = Toplevel()
    win.title("Login")
    win.geometry("300x250")

    tk.Label(win, text="Username").pack()
    user_entry = tk.Entry(win)
    user_entry.pack()

    tk.Label(win, text="Password").pack()
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()

    def do_login():
        username = user_entry.get()
        password = pass_entry.get()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        if row and bcrypt.checkpw(password.encode(), row[0]):
            messagebox.showinfo("Success", "Login Successful")
            win.destroy()
            open_dashboard()
        else:
            messagebox.showerror("Failed", "Invalid credentials")

    tk.Button(win, text="Login", command=do_login).pack(pady=10)
    tk.Button(win, text="Back", command=win.destroy).pack()

def signup_screen():
    win = Toplevel()
    win.title("Sign Up")
    win.geometry("300x250")

    tk.Label(win, text="Username").pack()
    user_entry = tk.Entry(win)
    user_entry.pack()

    tk.Label(win, text="Password").pack()
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()

    def do_signup():
        username = user_entry.get()
        password = pass_entry.get()
        if not username or not password:
            messagebox.showwarning("Error", "Fields required")
            return
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            conn.close()
            messagebox.showinfo("Done", "Signup successful!")
            win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    tk.Button(win, text="Sign Up", command=do_signup).pack(pady=10)
    tk.Button(win, text="Back", command=win.destroy).pack()

# -------------------------
# Main Window
# -------------------------
def main():
    root = tk.Tk()
    root.title("Smart Face Recognition")
    root.geometry("400x300")

    tk.Label(root, text="Group 13 Smart Face Recognition", font=("Arial", 14)).pack(pady=20)
    ttk.Button(root, text="Login", command=login_screen).pack(pady=10)
    ttk.Button(root, text="Sign Up", command=signup_screen).pack(pady=10)
    ttk.Button(root, text="Exit", command=root.quit).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
