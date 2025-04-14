import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
import bcrypt

# DB setup
conn = sqlite3.connect("SmartFaceRecognition.db")
cursor = conn.cursor()

def show_login_page():
    messagebox.showinfo("Redirect", "This would take you to the login page.")

def signup_page():
    root = tk.Tk()
    root.title("Sign Up")
    root.geometry("900x500")
    root.resizable(True, True)

    # Load background image
    try:
        bg_img = Image.open("FACE.png")
    except:
        bg_img = Image.new("RGB", (900, 700), "black")

    bg_img = bg_img.resize((900, 500), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Form frame
    form_frame = tk.Frame(root, bg="white", bd=2, relief="ridge")
    form_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(form_frame, text="Create your account", font=("Arial", 18, "bold"),
             bg="white", fg="green").pack(pady=(20, 5))
    tk.Label(form_frame, text="Please enter your details to sign up",
             font=("Times new roman", 10), bg="white").pack()

    inner = tk.Frame(form_frame, bg="white")
    inner.pack(pady=20)

    # Full Name
    tk.Label(inner, text="Full Name", bg="white", font=("Times new roman", 10)).grid(row=0, column=0, sticky='w')
    fullname_entry = tk.Entry(inner, width=30)
    fullname_entry.grid(row=1, column=0, pady=5)

    # Username
    tk.Label(inner, text="Username", bg="white", font=("Times new roman", 10)).grid(row=2, column=0, sticky='w')
    username_entry = tk.Entry(inner, width=30)
    username_entry.grid(row=3, column=0, pady=5)

    # Password
    tk.Label(inner, text="Password", bg="white", font=("Times new roman", 10)).grid(row=4, column=0, sticky='w')
    pw_frame = tk.Frame(inner, bg="white")
    pw_frame.grid(row=5, column=0, pady=5)
    password_entry = tk.Entry(pw_frame, width=28, show="*")
    password_entry.pack(side=tk.LEFT)

    def toggle_password():
        password_entry.config(show="" if password_entry.cget("show") == "*" else "*")
    tk.Button(pw_frame, text="👁", command=toggle_password, bg="white", bd=0).pack(side=tk.LEFT)

    # Confirm Password
    tk.Label(inner, text="Confirm Password", bg="white", font=("Times new roman", 10)).grid(row=6, column=0, sticky='w')
    cpw_frame = tk.Frame(inner, bg="white")
    cpw_frame.grid(row=7, column=0, pady=5)
    confirm_entry = tk.Entry(cpw_frame, width=28, show="*")
    confirm_entry.pack(side=tk.LEFT)

    def toggle_confirm():
        confirm_entry.config(show="" if confirm_entry.cget("show") == "*" else "*")
    tk.Button(cpw_frame, text="👁", command=toggle_confirm, bg="white", bd=0).pack(side=tk.LEFT)

    # Register button
    def signup():
        fullname = fullname_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get()
        confirm = confirm_entry.get()

        if not (fullname and username and password and confirm):
            messagebox.showwarning("Incomplete", "Please fill all fields.")
            return
        if password != confirm:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            cursor.execute("INSERT INTO Users (name, username, password, role) VALUES (?, ?, ?, 'admin')",
                           (fullname, username, hashed_pw))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            root.destroy()
            show_login_page()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")

    ttk.Button(form_frame, text="Sign Up", command=signup).pack(pady=10)

    tk.Label(form_frame, text="Already have an account?", bg="white", font=("Times new roman", 9)).pack()
    tk.Button(form_frame, text="Login here", bg="white", fg="blue", bd=0,
              font=("Times new roman", 9, "underline"),
              command=lambda: [root.destroy(), show_login_page()]).pack()

    tk.Label(form_frame, text="© 2025 - Group 13 Project", font=("Times new roman", 9),
             bg="white").pack(side=tk.BOTTOM, pady=(10, 5))

    root.mainloop()


# Launch the sign-up page
signup_page()
