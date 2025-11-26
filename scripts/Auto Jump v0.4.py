import pydirectinput
import threading
import time
import tkinter as tk
import ctypes
import webbrowser
import sys
from pynput import keyboard

# DESCRIPTION: Auto-Jump to sell Bubbles
# VERSIONS: all
version = "v1.0"
# ---------- SETTINGS ----------
JUMP_KEY = "space"
TOGGLE_KEY = "f2"
STOP_KEY = "f8"
TIP_URL = "https://ko-fi.com/Youngblock2k/tip"
JUMP_DELAY = 0.5  # seconds

# ---------- STATE ----------
running_flag = False
jump_count = 0
start_time = None
thread_active = True

# ---------- GUI ----------
root = tk.Tk()
root.overrideredirect(True)  # Remove frame
root.attributes("-topmost", True)
root.attributes("-alpha", 0.9)
root.configure(bg="black")

label = tk.Label(
    root,
    text="Inactive",
    font=("Arial", 14, "bold"),
    fg="red",
    bg="black"
)
label.pack(padx=10, pady=5)
root.geometry("+40+40")  # top-left corner

# ---------- FUNCTIONS ----------
def update_label():
    """Update GUI label text."""
    if running_flag:
        label.config(text=f"Active | Jumps: {jump_count}", fg="lime")
    else:
        label.config(text="Inactive", fg="red")

def jump_loop():
    """Continuously jump when active."""
    global jump_count, start_time
    while thread_active:
        if running_flag:
            if not start_time:
                start_time = time.time()
            pydirectinput.press(JUMP_KEY)
            jump_count += 1
            update_label()
            time.sleep(JUMP_DELAY)
        else:
            time.sleep(0.1)

def toggle_script():
    """Toggle pause/resume."""
    global running_flag
    running_flag = not running_flag
    update_label()
    if running_flag:
        print("Auto-Jump: Started")
    else:
        print("Auto-Jump: Paused")

def stop_script():
    """Stop completely."""
    global running_flag, thread_active
    running_flag = False
    thread_active = False

    # Calculate total time
    if start_time:
        elapsed = int(time.time() - start_time)
        hours = elapsed // 3600
        mins = (elapsed % 3600) // 60
        secs = elapsed % 60
        total_time = f"{hours:02}:{mins:02}:{secs:02}"
    else:
        total_time = "00:00:00"

    message = (
        f"Hello!\n\n"
        f"You used this macro for {total_time}.\n\n"
        f"If you enjoyed it, consider leaving a tip ❤️"
    )
    result = ctypes.windll.user32.MessageBoxW(0, message, "Thank You!", 0x1044)
    if result == 6:
        webbrowser.open(TIP_URL)
    root.destroy()
    sys.exit()

def key_listener():
    """Listen for F2 (toggle) and F8 (stop)."""
    def on_press(key):
        try:
            if key.name == TOGGLE_KEY:
                toggle_script()
            elif key.name == STOP_KEY:
                stop_script()
        except AttributeError:
            pass

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# ---------- THREADS ----------
threading.Thread(target=jump_loop, daemon=True).start()
threading.Thread(target=key_listener, daemon=True).start()

print("✅ Roblox Auto Jump Macro Loaded!")
print("▶ Press F2 to Start/Pause | Press F8 to Stop")

update_label()
root.mainloop()

