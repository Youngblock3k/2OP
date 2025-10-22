import time
import threading
import keyboard
import pydirectinput
import pyautogui
import tkinter as tk
import ctypes
import webbrowser
import sys
import os

running = False
start_time = None
thread_active = True

def spam_actions():
    """Auto jump + click loop"""
    global running
    last_jump = time.time()
    last_click = time.time()

    while thread_active:
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
    """Listens for F2 (toggle) and F3 (stop)"""
    global running, start_time, thread_active

    while thread_active:
        # F2 toggle on/off
        if keyboard.is_pressed("f2"):
            running = not running
            if running:
                label.config(text="Active", fg="lime")
                start_time = start_time or time.time()
                print("▶ Macro started")
            else:
                label.config(text="Inactive", fg="red")
                print("⏸ Macro paused")
            time.sleep(0.3)

        # F3 stop completely
        if keyboard.is_pressed("f3"):
            stop_script()
            break

        time.sleep(0.01)

def stop_script():
    """Stop macro and show popup"""
    global running, thread_active, start_time

    running = False
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

    # Popup message
    message = (
        f"Hello!\n\n"
        f"You used this macro for {total_time}.\n\n"
        f"If you enjoyed it, consider leaving a tip ❤️"
    )

    result = ctypes.windll.user32.MessageBoxW(
        0,
        message,
        "Macro Stopped",
        0x1044
    )

    if result == 6:  # "Yes"
        webbrowser.open("https://ko-fi.com/Youngblock2k/tip")

    print("\n🛑 Macro stopped")
    sys.exit()

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

# Console info
print("✅ Roblox Auto Bubble Macro Loaded!")
print("▶ Press F2 to Start/Pause | Press F3 to Stop")

# Threads
t1 = threading.Thread(target=spam_actions, daemon=True)
t1.start()

t2 = threading.Thread(target=hotkey_listener, daemon=True)
t2.start()

root.mainloop()
