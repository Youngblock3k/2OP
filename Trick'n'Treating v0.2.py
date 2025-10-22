import threading
import time
import ctypes
import sys
import webbrowser
import tkinter as tk
from ahk import AHK

ahk = AHK()

# ---------------- CONFIG ----------------
ON_SWITCH = "f2"       # Toggle start/stop
OFF_SWITCH = "f8"      # Stop + exit
JUMP_KEY = "space"
JUMP_DELAY = 0.5       # seconds
TIP_URL = "https://ko-fi.com/Youngblock2k/tip"

# ---------------- STATE ----------------
running_flag = False
jump_count = 0
total_time = "00:00:00"
start_time = None
thread_active = True

# ---------------- GUI ----------------
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.9)
root.configure(bg="black")
label = tk.Label(root, text="Inactive", font=("Arial", 14, "bold"), fg="red", bg="black")
label.pack(padx=10, pady=5)
root.geometry("+40+40")  # top-left corner

# ---------------- LOGIC ----------------
def update_label():
    """Update floating label text."""
    if running_flag:
        label.config(text=f"Active | Jumps: {jump_count}", fg="lime")
    else:
        label.config(text="Inactive", fg="red")

def jump_loop():
    """Main auto-jump thread."""
    global jump_count, start_time
    while thread_active:
        if running_flag:
            ahk.key_press(JUMP_KEY)
            jump_count += 1
            update_label()
            time.sleep(JUMP_DELAY)
        else:
            time.sleep(0.1)

def toggle_switch():
    """Toggle start/pause."""
    global running_flag, start_time
    running_flag = not running_flag
    if running_flag:
        if not start_time:
            start_time = time.time()
        print("Script started".ljust(60))
        update_label()
    else:
        print("Script paused".ljust(60))
        update_label()

def stop_script():
    """Completely stop the macro and show message box."""
    global running_flag, thread_active, total_time
    running_flag = False
    thread_active = False

    if start_time:
        elapsed = int(time.time() - start_time)
        hours = elapsed // 3600
        mins = (elapsed % 3600) // 60
        secs = elapsed % 60
        total_time = f"{hours:02}:{mins:02}:{secs:02}"

    msg = (
        f"Hello!\n\nYou have been using this macro for {total_time} hour(s).\n\n"
        f"These macros take a long time to make, so I'd be grateful if you left a tip :)"
    )
    result = ctypes.windll.user32.MessageBoxW(0, msg, "Thank you!", 0x1044)
    if result == 6:  # Yes button
        webbrowser.open(TIP_URL)
    root.destroy()
    sys.exit()

def key_listener():
    """Monitor for F2 and F8 keys."""
    from pynput import keyboard

    def on_press(key):
        try:
            if key.name == ON_SWITCH:
                toggle_switch()
            elif key.name == OFF_SWITCH:
                stop_script()
        except Exception:
            pass

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# ---------------- START ----------------
threading.Thread(target=jump_loop, daemon=True).start()
threading.Thread(target=key_listener, daemon=True).start()

print("Auto Jump Script Loaded! (F2 = Start/Pause, F8 = Stop + Exit)")
update_label()
root.mainloop()
