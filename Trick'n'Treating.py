import time
import threading
import pyautogui
import keyboard
import tkinter as tk

# ---------------- CONFIG ----------------
JUMP_KEY = "space"
JUMP_DELAY = 0.5  # seconds between jumps
RUNNING = False
JUMP_COUNT = 0

# ---------------- LOGIC ----------------
def auto_jump():
    global RUNNING, JUMP_COUNT
    while RUNNING:
        pyautogui.press(JUMP_KEY)
        JUMP_COUNT += 1
        update_label()
        time.sleep(JUMP_DELAY)

def start_jumping():
    global RUNNING
    if not RUNNING:
        RUNNING = True
        threading.Thread(target=auto_jump, daemon=True).start()
        status_label.config(text="Status: ACTIVE", fg="green")

def stop_jumping():
    global RUNNING
    RUNNING = False
    status_label.config(text="Status: INACTIVE", fg="red")

def toggle_jump(event=None):
    if RUNNING:
        stop_jumping()
    else:
        start_jumping()

# ---------------- UI ----------------
root = tk.Tk()
root.title("Roblox Auto Jump")
root.geometry("300x200")
root.resizable(False, False)

label = tk.Label(root, text="Jump Count: 0", font=("Arial", 18, "bold"))
label.pack(pady=20)

status_label = tk.Label(root, text="Status: INACTIVE", font=("Arial", 14, "bold"), fg="red")
status_label.pack()

def update_label():
    label.config(text=f"Jump Count: {JUMP_COUNT}")

start_btn = tk.Button(root, text="Start Jumping", font=("Arial", 12, "bold"), bg="gray", fg="white", command=start_jumping)
start_btn.pack(fill="x", padx=20, pady=5)

stop_btn = tk.Button(root, text="Stop Jumping", font=("Arial", 12, "bold"), bg="gray", fg="white", command=stop_jumping)
stop_btn.pack(fill="x", padx=20, pady=5)

root.bind("<F6>", toggle_jump)  # Press F6 to toggle auto-jump

root.mainloop()
