import tkinter as tk
from tkinter import ttk

def add():
    a = 10
    b = 20
    result = a + b
    result_label.config(text=f"Result: {result}")

root = tk.Tk()
root.title("Tkinter Demo")

label = ttk.Label(root, text="Hello, World!", font=("Arial", 24), foreground="blue")
label.pack(padx=20, pady=20)

label2 = ttk.Label(root, text="Click to calculate 10 + 20", font=("Helvetica", 12))
label2.pack(padx=20, pady=5)

button = ttk.Button(root, text="Add", command=add)
button.pack(padx=20, pady=10)

result_label = ttk.Label(root, text="", font=("Arial", 14, "bold"))
result_label.pack(pady=10)

root.mainloop()