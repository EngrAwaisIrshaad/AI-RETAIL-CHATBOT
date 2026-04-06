import tkinter as tk
from tkinter import scrolledtext, Entry, Button, Frame

def send_message():
    user_msg = entry_box.get()
    if user_msg:
        chat_area.config(state="normal")
        chat_area.insert(tk.END, f"You: {user_msg}\n")
        chat_area.insert(tk.END, f"Bot: Echo {user_msg}\n")
        chat_area.config(state="disabled")
        chat_area.yview(tk.END)
        entry_box.delete(0, tk.END)

root = tk.Tk()
root.title("Test GUI")
root.geometry("500x600")
root.configure(bg="#e5ddd5")

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#ffffff", font=("Arial", 12))
chat_area.pack(padx=10, pady=10, fill="both", expand=True)
chat_area.config(state="disabled")

entry_frame = Frame(root, bg="#e5ddd5")
entry_frame.pack(fill="x", padx=10, pady=10)

entry_box = Entry(entry_frame, font=("Arial", 14))
entry_box.pack(side="left", fill="x", expand=True, padx=(0,10))
entry_box.focus()
entry_box.bind("<Return>", lambda event: send_message())

send_button = Button(entry_frame, text="Send", command=send_message, bg="#128C7E", fg="white", font=("Arial",12))
send_button.pack(side="right")

root.mainloop()