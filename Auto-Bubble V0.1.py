import time
import threading
import keyboard
import pydirectinput
import pyautogui
import tkinter as tk

running = False

def spam_actions():
    global running
    last_jump = time.time()
    last_click = time.time()
    while True:
        if running:
            now = time.time()

            # Jump every 5 seconds
            if now - last_jump >= 5:
                pydirectinput.press("space")
                last_jump = now

            # Left click every 1 second
            if now - last_click >= 1:
                pyautogui.click()
                last_click = now

        time.sleep(0.01)

def hotkey_listener():
    global running
    while True:
        if keyboard.is_pressed("f2"):
            running = not running
            label.config(
                text="Active" if running else "Inactive",
                fg="lime" if running else "red"
            )
            time.sleep(0.3)

        time.sleep(0.01)

# --- UI ---
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.9)
root.configure(bg="black")

label = tk.Label(
    root, text="Inactive", font=("Arial", 14, "bold"),
    fg="red", bg="black"
)
label.pack(padx=10, pady=5)

root.geometry("+40+40")

# Threads
t1 = threading.Thread(target=spam_actions, daemon=True)
t1.start()

t2 = threading.Thread(target=hotkey_listener, daemon=True)
t2.start()

root.mainloop()
