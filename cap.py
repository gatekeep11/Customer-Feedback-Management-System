import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ----------------- Database Setup ----------------- #
conn = sqlite3.connect("feedback_system.db")
cursor = conn.cursor()

# Create customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    address TEXT,
    joined_date TEXT
)
""")

# Create feedbacks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS feedbacks (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    feedback TEXT NOT NULL,
    rating INTEGER,
    category TEXT,
    date_submitted TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
""")
conn.commit()

# ----------------- GUI Setup ----------------- #
root = tk.Tk()
root.title("💬 Customer Feedback Management System")
root.geometry("950x700")
root.config(bg="#F8FAFF")

# ----------------- Functions ----------------- #
def add_customer():
    name = name_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()
    address = address_entry.get()
    joined_date = datetime.now().strftime("%Y-%m-%d")

    if not name or not email:
        messagebox.showwarning("⚠️ Missing Data", "Name and Email are required.")
        return

    try:
        cursor.execute("INSERT INTO customers (name, email, phone, address, joined_date) VALUES (?, ?, ?, ?, ?)",
                       (name, email, phone, address, joined_date))
        conn.commit()
        messagebox.showinfo("✅ Success", "Customer added successfully!")
        load_customers()
        clear_entries()
    except sqlite3.IntegrityError:
        messagebox.showerror("❌ Error", "This email is already registered.")

def add_feedback():
    selected = customer_tree.focus()
    if not selected:
        messagebox.showwarning("⚠️ Selection Error", "Select a customer first.")
        return
    data = customer_tree.item(selected)
    customer_id = data["values"][0]
    feedback_text = feedback_entry.get("1.0", tk.END).strip()
    rating = rating_var.get()
    category = category_var.get()
    date_submitted = datetime.now().strftime("%Y-%m-%d")

    if not feedback_text:
        messagebox.showwarning("⚠️ Missing Data", "Please enter feedback text.")
        return

    cursor.execute("INSERT INTO feedbacks (customer_id, feedback, rating, category, date_submitted) VALUES (?, ?, ?, ?, ?)",
                   (customer_id, feedback_text, rating, category, date_submitted))
    conn.commit()
    messagebox.showinfo("✅ Success", "Feedback added successfully!")
    feedback_entry.delete("1.0", tk.END)
    view_feedbacks()

def load_customers():
    for row in customer_tree.get_children():
        customer_tree.delete(row)
    cursor.execute("SELECT * FROM customers")
    for row in cursor.fetchall():
        customer_tree.insert("", tk.END, values=row)

def view_feedbacks():
    for row in feedback_tree.get_children():
        feedback_tree.delete(row)
    cursor.execute("""
    SELECT f.feedback_id, c.name, c.email, f.category, f.rating, f.feedback, f.date_submitted
    FROM feedbacks f
    JOIN customers c ON f.customer_id = c.customer_id
    """)
    for row in cursor.fetchall():
        feedback_tree.insert("", tk.END, values=row)

def delete_feedback():
    selected = feedback_tree.focus()
    if not selected:
        messagebox.showwarning("⚠️ Selection Error", "Select a feedback to delete.")
        return
    data = feedback_tree.item(selected)
    feedback_id = data["values"][0]
    cursor.execute("DELETE FROM feedbacks WHERE feedback_id=?", (feedback_id,))
    conn.commit()
    messagebox.showinfo("🗑️ Deleted", "Feedback deleted successfully!")
    view_feedbacks()

def delete_customer():
    selected = customer_tree.focus()
    if not selected:
        messagebox.showwarning("⚠️ Selection Error", "Select a customer to delete.")
        return
    data = customer_tree.item(selected)
    customer_id = data["values"][0]

    confirm = messagebox.askyesno("⚠️ Confirm Delete", "Are you sure you want to delete this customer and all their feedbacks?")
    if not confirm:
        return

    # Delete all feedbacks of the customer first
    cursor.execute("DELETE FROM feedbacks WHERE customer_id=?", (customer_id,))
    # Delete customer record
    cursor.execute("DELETE FROM customers WHERE customer_id=?", (customer_id,))
    conn.commit()
    messagebox.showinfo("🗑️ Deleted", "Customer and all their feedbacks deleted successfully!")
    load_customers()
    view_feedbacks()

def clear_entries():
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    feedback_entry.delete("1.0", tk.END)

# ----------------- GUI Layout ----------------- #
tk.Label(root, text="Customer Feedback Management System", font=("Segoe UI Semibold", 20), bg="#F8FAFF", fg="#334B77").pack(pady=10)

# Customer Input Frame
customer_frame = tk.LabelFrame(root, text="Add Customer Details", bg="#F8FAFF", fg="#334B77", font=("Segoe UI", 10, "bold"))
customer_frame.pack(fill="x", padx=20, pady=5)

tk.Label(customer_frame, text="Name:", bg="#F8FAFF").grid(row=0, column=0, padx=5, pady=5, sticky="e")
name_entry = ttk.Entry(customer_frame, width=25)
name_entry.grid(row=0, column=1)

tk.Label(customer_frame, text="Email:", bg="#F8FAFF").grid(row=0, column=2, padx=5, pady=5, sticky="e")
email_entry = ttk.Entry(customer_frame, width=25)
email_entry.grid(row=0, column=3)

tk.Label(customer_frame, text="Phone:", bg="#F8FAFF").grid(row=1, column=0, padx=5, pady=5, sticky="e")
phone_entry = ttk.Entry(customer_frame, width=25)
phone_entry.grid(row=1, column=1)

tk.Label(customer_frame, text="Address:", bg="#F8FAFF").grid(row=1, column=2, padx=5, pady=5, sticky="e")
address_entry = ttk.Entry(customer_frame, width=25)
address_entry.grid(row=1, column=3)

tk.Button(customer_frame, text="Add Customer", bg="#4CAF50", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=add_customer).grid(row=0, column=4, rowspan=2, padx=15)
tk.Button(customer_frame, text="Delete Selected Customer", bg="#E57373", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=delete_customer).grid(row=0, column=5, rowspan=2, padx=10)

# Customer Table
tk.Label(root, text="Customer List", bg="#F8FAFF", font=("Segoe UI Semibold", 12)).pack()
customer_tree = ttk.Treeview(root, columns=("ID", "Name", "Email", "Phone", "Address", "Joined"), show="headings", height=5)
customer_tree.pack(fill="x", padx=20)
for col in ("ID", "Name", "Email", "Phone", "Address", "Joined"):
    customer_tree.heading(col, text=col)
    customer_tree.column(col, width=140)
load_customers()

# Feedback Frame
feedback_frame = tk.LabelFrame(root, text="Add Feedback", bg="#F8FAFF", fg="#334B77", font=("Segoe UI", 10, "bold"))
feedback_frame.pack(fill="x", padx=20, pady=10)

tk.Label(feedback_frame, text="Category:", bg="#F8FAFF").grid(row=0, column=0, padx=5, pady=5)
category_var = tk.StringVar()
category_box = ttk.Combobox(feedback_frame, textvariable=category_var, values=["Product", "Service", "Support", "Other"], width=15)
category_box.grid(row=0, column=1)
category_box.current(0)

tk.Label(feedback_frame, text="Rating:", bg="#F8FAFF").grid(row=0, column=2, padx=5, pady=5)
rating_var = tk.IntVar()
rating_box = ttk.Combobox(feedback_frame, textvariable=rating_var, values=[1,2,3,4,5], width=5)
rating_box.grid(row=0, column=3)
rating_box.current(4)

feedback_entry = tk.Text(feedback_frame, width=80, height=3)
feedback_entry.grid(row=1, column=0, columnspan=4, padx=10, pady=5)

tk.Button(feedback_frame, text="Submit Feedback", bg="#5C6BC0", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=add_feedback).grid(row=1, column=4, padx=10)
tk.Button(feedback_frame, text="Delete Selected Feedback", bg="#E57373", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=delete_feedback).grid(row=1, column=5, padx=10)

# Feedback Table
tk.Label(root, text="Feedback Records", bg="#F8FAFF", font=("Segoe UI Semibold", 12)).pack()
feedback_tree = ttk.Treeview(root, columns=("ID", "Name", "Email", "Category", "Rating", "Feedback", "Date"), show="headings", height=7)
feedback_tree.pack(fill="x", padx=20)
for col in ("ID", "Name", "Email", "Category", "Rating", "Feedback", "Date"):
    feedback_tree.heading(col, text=col)
    feedback_tree.column(col, width=130 if col!="Feedback" else 200)

# ----------------- Run ----------------- #
view_feedbacks()
root.mainloop()
