import tkinter as tk
from tkinter import ttk
import requests
import threading
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

# === Load persona name from YAML ===
load_dotenv()
PERSONA_PATH = os.getenv("PERSONA_PATH", "app/config/characters/default_persona.yml")

def get_persona_name(path: str) -> str:
    try:
        with open(Path(path), "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("name", "Assistant")
    except Exception:
        return "Assistant"

persona_name = get_persona_name(PERSONA_PATH)

# === Create main window ===
root = tk.Tk()
root.title("NeuraForm - AI Chat")
root.geometry("600x500")
root.configure(bg="#eaeaea")

# === Chat display using Canvas ===
chat_frame = tk.Frame(root)
chat_frame.pack(fill='both', expand=True)

canvas = tk.Canvas(chat_frame, bg="#eaeaea", highlightthickness=0)
scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#eaeaea")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# === Entry field ===
entry = tk.Entry(root, font=("Segoe UI", 10))
entry.pack(padx=10, pady=(0, 10), fill='x')

def create_bubble(message, sender="user"):
    outer_frame = tk.Frame(scrollable_frame, bg="#eaeaea")

    name = "You" if sender == "user" else persona_name
    bg_color = "#ffffff" if sender == "user" else "#fceaff"
    fg_color = "#000000" if sender == "user" else "#5c2a7d"
    anchor_side = "e" if sender == "user" else "w"


    # Wrap in alignment frame with full width
    align_frame = tk.Frame(outer_frame, bg="#eaeaea", width=canvas.winfo_width())
    align_frame.pack(fill='x', expand=True)

    # Name label
    name_label = tk.Label(
        align_frame, text=f"{name}:", font=("Segoe UI", 8, "bold"),
        fg=fg_color, bg="#eaeaea"
    )
    name_label.pack(anchor=anchor_side, padx=10)

    # Message label
    message_label = tk.Label(
        align_frame, text=message, font=("Segoe UI", 10),
        fg=fg_color, bg=bg_color, wraplength=300,
        justify="left", padx=12, pady=8
    )
    message_label.pack(anchor=anchor_side, padx=10)

    outer_frame.pack(fill='x', pady=5)
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

def send_message():
    message = entry.get().strip()
    if not message:
        return

    create_bubble(message, sender="user")
    entry.delete(0, 'end')
    threading.Thread(target=fetch_reply, args=(message,)).start()


def fetch_reply(message):
    try:
        response = requests.post(
            "http://localhost:8000/chat/",
            json={
                "user_id": "demo-user",
                "message": message,
                "mode": "safe"
            }
        )
        if response.status_code == 200:
            reply = response.json().get("reply", "")
        else:
            reply = f"(Error {response.status_code})"
    except Exception as e:
        reply = f"(Request failed: {e})"

    create_bubble(reply, sender="ai")


# === Button + Enter ===
send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(padx=10, pady=(0, 10))
entry.bind("<Return>", lambda event: send_message())

# === Run UI ===
root.mainloop()
