import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import cv2
import bcrypt
from PIL import Image, ImageTk
import re

# --- DATABASE SETUP ---
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin'
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS UserDetails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_no TEXT NOT NULL,
    full_name TEXT NOT NULL,
    year TEXT NOT NULL
)
""")
conn.commit()

current_user = {"username": None, "role": None}


# --- UTILS ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


# --- USER DETAILS FORM ---
def user_details_form():
    form = tk.Tk()
    form.title("Insert User Details")
    form.geometry("400x350")
    form.config(bg="lightgray")

    tk.Label(form, text="Insert User Details", font=("Times new roman", 14, "bold"), bg="lightgray").pack(pady=10)

    tk.Label(form, text="Reg No:", bg="lightgray").pack()
    reg_entry = tk.Entry(form, width=40)
    reg_entry.pack()

    tk.Label(form, text="Full Name:", bg="lightgray").pack()
    name_entry = tk.Entry(form, width=40)
    name_entry.pack()

    tk.Label(form, text="Year:", bg="lightgray").pack()
    year_entry = tk.Entry(form, width=40)
    year_entry.pack()

    def save_details():
        reg = reg_entry.get().strip()
        name = name_entry.get().strip()
        year = year_entry.get().strip()

        if not reg or not name or not year:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            cursor.execute("INSERT INTO UserDetails (reg_no, full_name, year) VALUES (?, ?, ?)", (reg, name, year))
            conn.commit()
            messagebox.showinfo("Saved", "User details inserted successfully")
            form.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save user details: {e}")

    ttk.Button(form, text="Save", command=save_details).pack(pady=20)
    form.mainloop()


# --- FACE RECOGNITION ---
def launch_face_recognition(username):
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"{username}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Face Recognition - Press 'q' to Exit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    user_details_form()


# --- LOGOUT ---
def logout(window):
    global current_user
    current_user = {"username": None, "role": None}
    window.destroy()
    show_login_page()


# --- LOGIN PAGE ---
def show_login_page():
    login_window = tk.Tk()
    login_window.title("Admin Login")
    login_window.geometry("900x500")

    style = ttk.Style(login_window)
    style.theme_use("clam")
    style.configure("Hover.TButton", background="green", foreground="white", font=("Times new roman", 12))
    style.map("Hover.TButton", background=[("active", "#228B22")])

    container = tk.Frame(login_window)
    container.pack(fill=tk.BOTH, expand=True)

    left_frame = tk.Frame(container, width=450, height=500)
    left_frame.grid(row=0, column=0, sticky="nsew")

    right_frame = tk.Frame(container, bg="Lightgray", width=450, height=500)
    right_frame.grid(row=0, column=1, sticky="nsew")

    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=1)
    container.grid_rowconfigure(0, weight=1)

    try:
        bg_img = Image.open(r"C:\Users\julie\Downloads\SmartFaceRecognition\assets\FACE.png")
    except:
        bg_img = Image.new("RGB", (450, 500), "black")

    bg_img = bg_img.resize((450, 500), Image.Resampling.LANCZOS)

    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(left_frame, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(left_frame, text="GROUP 13 SMART FACE RECOGNITION", fg="white", bg="black",
             font=("Arial", 14, "bold")).place(x=45, y=440)

    tk.Label(right_frame, text="Hi, welcome back", font=("Arial", 18, "bold"),
             bg="Lightgray", fg="green").pack(pady=(40, 5))
    tk.Label(right_frame, text="Please fill in your details to log in", font=("Times new roman", 10),
             bg="Lightgray").pack()

    form_frame = tk.Frame(right_frame, bg="Lightgray")
    form_frame.pack(pady=30)

    tk.Label(form_frame, text="Username", bg="Lightgray", font=("Times new roman", 10)).grid(row=0, column=0, sticky='w')
    cursor.execute("SELECT username FROM Users WHERE role='admin'")
    usernames = [row[0] for row in cursor.fetchall()]
    username_var = tk.StringVar()
    username_dropdown = ttk.Combobox(form_frame, textvariable=username_var, values=usernames, state="readonly", width=28)
    username_dropdown.grid(row=1, column=0, pady=5)
    username_dropdown.set("Select username")

    tk.Label(form_frame, text="Password", bg="Lightgray", font=("Times new roman", 10)).grid(row=2, column=0, sticky='w')
    pw_frame = tk.Frame(form_frame)
    pw_frame.grid(row=3, column=0, pady=5)
    password_entry = tk.Entry(pw_frame, width=27, show="*")
    password_entry.pack(side=tk.LEFT)

    def toggle_pw():
        password_entry.config(show="" if password_entry.cget("show") == "*" else "*")
    tk.Button(pw_frame, text="👁", command=toggle_pw).pack(side=tk.LEFT)

    remember_var = tk.IntVar()
    tk.Checkbutton(form_frame, text="Remember me", variable=remember_var, bg="Lightgray").grid(row=4, column=0, sticky='w', pady=10)

    def login():
        username = username_var.get().strip()
        password = password_entry.get().strip()
        cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
        user = cursor.fetchone()
        if user and verify_password(password, user[3]):
            if user[4] != "admin":
                messagebox.showerror("Access Denied", "Only admins can log in to this system.")
                return
            global current_user
            current_user["username"] = user[2]
            current_user["role"] = user[4]
            login_window.destroy()
            open_main_app(user)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def open_main_app(user):
        main_app = tk.Tk()
        main_app.title(f"Admin Panel - {user[1]}")
        main_app.geometry("400x300")
        tk.Label(main_app, text=f"Welcome {user[1]}", font=("Times new roman", 14)).pack(pady=20)
        ttk.Button(main_app, text="Start Face Recognition", style="Hover.TButton",
                   command=lambda: [main_app.destroy(), launch_face_recognition(user[2])]).pack(pady=10)
        ttk.Button(main_app, text="Logout", style="Hover.TButton",
                   command=lambda: logout(main_app)).pack(pady=10)
        main_app.mainloop()

    ttk.Button(right_frame, text="Login", style="Hover.TButton", command=login).pack(pady=10)

    tk.Label(right_frame, text="Don't have an account?", bg="Lightgray", font=("Times new roman", 9)).pack()
    tk.Button(right_frame, text="Sign up here", bg="Lightgray", fg="blue", bd=0,
              font=("Times new roman", 9, "underline"),
              command=lambda: [login_window.destroy(), show_signup_page()]).pack()

    tk.Label(right_frame, text="© 2025 - Group 13 Project", font=("Times new roman", 9), bg="Lightgray").pack(side=tk.BOTTOM, pady=15)
    login_window.mainloop()


# --- SIGNUP PAGE ---
def show_signup_page():
    signup_window = tk.Tk()
    signup_window.title("Sign Up")
    signup_window.geometry("400x400")
    signup_window.config(bg="lightgray")

    tk.Label(signup_window, text="Create Admin Account", font=("Arial", 14, "bold"), bg="lightgray").pack(pady=20)

    tk.Label(signup_window, text="Name", bg="lightgray").pack()
    name_entry = tk.Entry(signup_window, width=30)
    name_entry.pack(pady=5)

    tk.Label(signup_window, text="Username", bg="lightgray").pack()
    username_entry = tk.Entry(signup_window, width=30)
    username_entry.pack(pady=5)

    tk.Label(signup_window, text="Password", bg="lightgray").pack()
    password_entry = tk.Entry(signup_window, show="*", width=30)
    password_entry.pack(pady=5)

    tk.Label(signup_window, text="Confirm Password", bg="lightgray").pack()
    confirm_pw_entry = tk.Entry(signup_window, show="*", width=30)
    confirm_pw_entry.pack(pady=5)

    def signup():
        name = name_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        confirm_pw = confirm_pw_entry.get().strip()

        if not name or not username or not password or not confirm_pw:
            messagebox.showerror("Error", "All fields are required")
            return

        if password != confirm_pw:
            messagebox.showerror("Error", "Passwords do not match")
            return

        hashed_pw = hash_password(password)

        try:
            cursor.execute("INSERT INTO Users (name, username, password) VALUES (?, ?, ?)",
                           (name, username, hashed_pw))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully")
            signup_window.destroy()
            show_login_page()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    ttk.Button(signup_window, text="Sign Up", command=signup).pack(pady=20)
    signup_window.mainloop()


# --- START APP ---
show_login_page()
