import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# --- DB SETUP ---
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS UserDetails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_no TEXT NOT NULL,
    full_name TEXT NOT NULL,
    year TEXT NOT NULL
)""")
conn.commit()

# --- USER MANAGEMENT PAGE ---
def show_user_management_page():
    def load_data():
        for i in tree.get_children():
            tree.delete(i)
        cursor.execute("SELECT * FROM UserDetails")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

    def search():
        query = search_var.get().strip()
        if not query:
            load_data()
            return
        for i in tree.get_children():
            tree.delete(i)
        cursor.execute("SELECT * FROM UserDetails WHERE reg_no LIKE ? OR full_name LIKE ?", 
                       (f"%{query}%", f"%{query}%"))
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

    def filter_year(event):
        selected_year = year_filter.get()
        if selected_year == "All":
            load_data()
            return
        for i in tree.get_children():
            tree.delete(i)
        cursor.execute("SELECT * FROM UserDetails WHERE year=?", (selected_year,))
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a row to delete")
            return
        item = tree.item(selected)
        record_id = item['values'][0]
        cursor.execute("DELETE FROM UserDetails WHERE id=?", (record_id,))
        conn.commit()
        load_data()
        messagebox.showinfo("Deleted", "Record deleted successfully")

    def edit_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a row to edit")
            return
        item = tree.item(selected)
        data = item['values']

        edit_win = tk.Toplevel(window)
        edit_win.title("Edit User")
        edit_win.geometry("350x300")
        edit_win.config(bg="lightgray")

        tk.Label(edit_win, text="Edit User Details", font=("Times new roman", 14, "bold"), bg="lightgray").pack(pady=10)

        tk.Label(edit_win, text="Reg No:", bg="lightgray").pack()
        reg_entry = tk.Entry(edit_win, width=30)
        reg_entry.pack()
        reg_entry.insert(0, data[1])

        tk.Label(edit_win, text="Full Name:", bg="lightgray").pack()
        name_entry = tk.Entry(edit_win, width=30)
        name_entry.pack()
        name_entry.insert(0, data[2])

        tk.Label(edit_win, text="Year:", bg="lightgray").pack()
        year_entry = tk.Entry(edit_win, width=30)
        year_entry.pack()
        year_entry.insert(0, data[3])

        def update():
            new_reg = reg_entry.get().strip()
            new_name = name_entry.get().strip()
            new_year = year_entry.get().strip()
            if not new_reg or not new_name or not new_year:
                messagebox.showerror("Error", "All fields required")
                return
            cursor.execute("UPDATE UserDetails SET reg_no=?, full_name=?, year=? WHERE id=?",
                           (new_reg, new_name, new_year, data[0]))
            conn.commit()
            load_data()
            messagebox.showinfo("Success", "User updated successfully")
            edit_win.destroy()

        ttk.Button(edit_win, text="Update", command=update).pack(pady=20)

    # --- UI ---
    window = tk.Tk()
    window.title("User Details Management")
    window.geometry("800x500")
    window.config(bg="lightgray")

    top_frame = tk.Frame(window, bg="lightgray")
    top_frame.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(top_frame, text="Search:", bg="lightgray").pack(side=tk.LEFT)
    search_var = tk.StringVar()
    tk.Entry(top_frame, textvariable=search_var, width=30).pack(side=tk.LEFT, padx=5)
    ttk.Button(top_frame, text="Search", command=search).pack(side=tk.LEFT)

    tk.Label(top_frame, text="  Filter by Year:", bg="lightgray").pack(side=tk.LEFT, padx=10)
    year_filter = ttk.Combobox(top_frame, values=["All"] + [str(y) for y in range(2020, 2031)], state="readonly", width=10)
    year_filter.set("All")
    year_filter.pack(side=tk.LEFT)
    year_filter.bind("<<ComboboxSelected>>", filter_year)

    tree = ttk.Treeview(window, columns=("ID", "Reg No", "Full Name", "Year"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Reg No", text="Reg No")
    tree.heading("Full Name", text="Full Name")
    tree.heading("Year", text="Year")
    tree.column("ID", width=50, anchor='center')
    tree.column("Reg No", width=150)
    tree.column("Full Name", width=300)
    tree.column("Year", width=100, anchor='center')
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    btn_frame = tk.Frame(window, bg="lightgray")
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Edit Selected", command=edit_selected).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Delete Selected", command=delete_selected).pack(side=tk.LEFT)

    load_data()
    window.mainloop()

# --- LAUNCH PAGE ---
if __name__ == "__main__":
    show_user_management_page()
