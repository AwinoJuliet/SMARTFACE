import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import cv2
import bcrypt
from PIL import Image, ImageTk

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
    form.config(bg="skyblue")

    tk.Label(form, text="Insert User Details", font=("Times new roman", 14, "bold"), bg="skyblue").pack(pady=10)

    tk.Label(form, text="Reg No:", bg="skyblue").pack()
    reg_entry = tk.Entry(form, width=40)
    reg_entry.pack()

    tk.Label(form, text="Full Name:", bg="skyblue").pack()
    name_entry = tk.Entry(form, width=40)
    name_entry.pack()

    tk.Label(form, text="Year:", bg="skyblue").pack()
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

    right_frame = tk.Frame(container, bg="skyblue", width=450, height=500)
    right_frame.grid(row=0, column=1, sticky="nsew")

    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=1)
    container.grid_rowconfigure(0, weight=1)

    try:
        bg_img = Image.open("FACE.png")
    except:
        bg_img = Image.new("RGB", (800, 800), "black")

    bg_img = bg_img.resize((800, 800), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(left_frame, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # --- Moving Label Animation ---
    text_label = tk.Label(left_frame, text="GROUP 13 SMART FACE RECOGNITION PROJECT", fg="white", bg="black",
                          font=("Arial", 14, "bold"))
    text_label.place(x=45, y=440)

    dx, dy = 2, 2
    max_x, max_y = 350, 450
    min_x, min_y = 0, 0

    def animate_text():
        nonlocal dx, dy
        x = text_label.winfo_x()
        y = text_label.winfo_y()
        if x + dx > max_x or x + dx < min_x:
            dx = -dx
        if y + dy > max_y or y + dy < min_y:
            dy = -dy
        text_label.place(x=x + dx, y=y + dy)
        left_frame.after(30, animate_text)

    animate_text()

    # --- RIGHT FRAME CONTENT ---
    try:
        logo_img = Image.open("FACE 1.png")
        logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(right_frame, image=logo_photo, bg="skyblue")
        logo_label.image = logo_photo
        logo_label.pack(pady=(30, 10))
    except Exception as e:
        print("Error loading logo:", e)

    tk.Label(right_frame, text="Hi, welcome back", font=("Arial", 18, "bold"),
             bg="skyblue", fg="green").pack(pady=(0, 5))
    tk.Label(right_frame, text="Please fill in your details to log in", font=("Times new roman", 10),
             bg="skyblue").pack()

    form_frame = tk.Frame(right_frame, bg="skyblue")
    form_frame.pack(pady=30)

    tk.Label(form_frame, text="Username", bg="skyblue", font=("Times new roman", 10)).grid(row=0, column=0, sticky='w')
    cursor.execute("SELECT username FROM Users WHERE role='admin'")
    usernames = [row[0] for row in cursor.fetchall()]
    username_var = tk.StringVar()
    username_dropdown = ttk.Combobox(form_frame, textvariable=username_var, values=usernames, state="readonly", width=28)
    username_dropdown.grid(row=1, column=0, pady=5)
    username_dropdown.set("Select username")

    tk.Label(form_frame, text="Password", bg="skyblue", font=("Times new roman", 10)).grid(row=2, column=0, sticky='w')
    pw_frame = tk.Frame(form_frame)
    pw_frame.grid(row=3, column=0, pady=5)
    password_entry = tk.Entry(pw_frame, width=27, show="*")
    password_entry.pack(side=tk.LEFT)

    def toggle_pw():
        password_entry.config(show="" if password_entry.cget("show") == "*" else "*")
    tk.Button(pw_frame, text="👁", command=toggle_pw).pack(side=tk.LEFT)

    remember_var = tk.IntVar()
    tk.Checkbutton(form_frame, text="Remember me", variable=remember_var, bg="skyblue").grid(row=4, column=0, sticky='w', pady=10)

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

    tk.Label(right_frame, text="Don't have an account?", bg="skyblue", font=("Times new roman", 9)).pack()
    tk.Button(right_frame, text="Sign up here", bg="skyblue", fg="blue", bd=0,
              font=("Times new roman", 9, "underline"),
              command=lambda: [login_window.destroy(), show_signup_page()]).pack()

    tk.Label(right_frame, text="© 2025 - Group 13 Project", font=("Times new roman", 9), bg="skyblue").pack(side=tk.BOTTOM, pady=15)

    login_window.mainloop()


# --- SIGNUP PAGE ---
def show_signup_page():
    signup_window = tk.Tk()
    signup_window.title("Sign Up")
    signup_window.geometry("400x460")
    signup_window.config(bg="skyblue")

    style = ttk.Style(signup_window)
    style.theme_use("clam")
    style.configure("Hover.TButton", background="#228B22", foreground="white", font=("Arial", 11))
    style.map("Hover.TButton", background=[("active", "#006400")])

    tk.Label(signup_window, text="Create Admin Account", font=("Arial", 16, "bold"), bg="skyblue", fg="green").pack(pady=15)

    tk.Label(signup_window, text="Name", bg="skyblue").pack()
    name_entry = tk.Entry(signup_window, width=32)
    name_entry.pack(pady=5)

    tk.Label(signup_window, text="Username", bg="skyblue").pack()
    username_entry = tk.Entry(signup_window, width=32)
    username_entry.pack(pady=5)

    tk.Label(signup_window, text="Staff Number", bg="skyblue").pack()
    staffno_entry = tk.Entry(signup_window, width=32)
    staffno_entry.pack(pady=5)

    tk.Label(signup_window, text="Password", bg="skyblue").pack()
    pw_frame = tk.Frame(signup_window, bg="skyblue")
    pw_frame.pack(pady=5)
    password_entry = tk.Entry(pw_frame, width=27, show="*")
    password_entry.pack(side=tk.LEFT)
    tk.Button(pw_frame, text="👁", command=lambda: toggle_password(password_entry)).pack(side=tk.LEFT)

    tk.Label(signup_window, text="Confirm Password", bg="skyblue").pack()
    confirm_frame = tk.Frame(signup_window, bg="skyblue")
    confirm_frame.pack(pady=5)
    confirm_pw_entry = tk.Entry(confirm_frame, width=27, show="*")
    confirm_pw_entry.pack(side=tk.LEFT)
    tk.Button(confirm_frame, text="👁", command=lambda: toggle_password(confirm_pw_entry)).pack(side=tk.LEFT)

    def toggle_password(entry_widget):
        entry_widget.config(show="" if entry_widget.cget("show") == "*" else "*")

    def signup():
        name = name_entry.get().strip()
        username = username_entry.get().strip()
        staff_no = staffno_entry.get().strip()
        password = password_entry.get().strip()
        confirm_pw = confirm_pw_entry.get().strip()

        if not name or not username or not staff_no or not password or not confirm_pw:
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

    ttk.Button(signup_window, text="Sign Up", style="Hover.TButton", command=signup).pack(pady=20)

    tk.Label(signup_window, text="Already have an account?", bg="skyblue", font=("Times new roman", 9)).pack()
    tk.Button(signup_window, text="Login here", bg="skyblue", fg="blue", bd=0,
              font=("Times new roman", 9, "underline"),
              cursor="hand2", command=lambda: [signup_window.destroy(), show_login_page()]).pack()

    signup_window.mainloop()


# --- START APP ---
show_login_page()
