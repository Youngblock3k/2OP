from pynput import keyboard
from PIL import ImageGrab
import pydirectinput
import numpy as np
import threading
import time
import cv2
import sys
import os
import functools
import ctypes
import tkinter as tk
from tkinter import ttk

# DESCRIPTION: Faster egg hatching and hatched eggs counter with GUI overlay
# VERSIONS: all
print = functools.partial(print, flush=True)

# global names
ON_switch = keyboard.Key.f2
OFF_switch = keyboard.Key.f3

running_flag = False    
total_time = ""
hatched_eggs = 0
send_once = False
daily_col = (238, 50, 94)
gui = None

# Auto resolution detection
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Set coordinates based on detected resolution
if screen_width == 2560 and screen_height == 1440:
    daily = (68, 695)
elif screen_width == 1920 and screen_height == 1080:
    daily = (59, 514) 
elif screen_width in [1366, 1364] and screen_height == 768:
    daily = (47, 362)
else:
    ctypes.windll.user32.MessageBoxW(
        0,
        f"Please either use 2560x1440, 1920x1080 or 1366x768 resolution and set your scale to 100% for this macro to work.\nCurrent resolution: {screen_width}x{screen_height}",
        "Invalid resolution",
        0x10
    )
    sys.exit()

# GUI Overlay class
class EggCounterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Egg Counter")
        self.root.geometry("260x60+0+0")
        self.root.configure(bg='#F5F5DC')
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.offset_x = 0
        self.offset_y = 0

        self.main_frame = tk.Frame(
            self.root,
            bg='#F5F5DC',
            relief='solid',
            bd=2,
            highlightbackground='#D2B48C',
            highlightthickness=2
        )
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.egg_label = tk.Label(
            self.main_frame, 
            text="Eggs Hatched: 0", 
            font=("Arial", 12, "bold"),
            bg='#F5F5DC', 
            fg='#8B4513',
            padx=10,
            pady=15
        )
        self.egg_label.pack(side='left', fill='both', expand=True)

        self.close_btn = tk.Label(
            self.main_frame,
            text="×",
            font=("Arial", 12, "bold"),
            bg='#CD5C5C',
            fg='white',
            cursor='hand2',
            width=2,
            height=1
        )
        self.close_btn.pack(side='right', padx=5)
        self.close_btn.bind('<Button-1>', self.close)
        self.main_frame.bind('<Button-1>', self.s_drag)
        self.main_frame.bind('<B1-Motion>', self.drag)
        self.egg_label.bind('<Button-1>', self.s_drag)
        self.egg_label.bind('<B1-Motion>', self.drag)
        self.root.bind('<Button-1>', self.s_drag)
        self.root.bind('<B1-Motion>', self.drag)
    
    def s_drag(self, event):
        self.offset_x = event.x_root - self.root.winfo_x()
        self.offset_y = event.y_root - self.root.winfo_y()
    
    def drag(self, event):
        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y
        self.root.geometry(f"+{x}+{y}")
    
    def egg_counter(self, count):
        if self.root and self.egg_label:
            try:
                self.egg_label.config(text=f"Eggs Hatched: {count}")
                self.root.update_idletasks()
            except tk.TclError:
                pass
    
    def close(self, event):
        self.root.quit()
        sys.exit()

# function to format elapsed time into hh:mm:ss
def format_time_ignore(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# function to update session time in the background
def update_session_time_ignore():
    global total_time
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        total_time = format_time_ignore(elapsed_time)
        time.sleep(1)

# Start the session time update thread
session_time_thread = threading.Thread(target=update_session_time_ignore, daemon=True)
session_time_thread.start()

# clearing the cmd
def cls():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def detect_color(coords, target_color, tolerance=20):
    screenshot = ImageGrab.grab()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    bgr_color = img[coords[1], coords[0]]
    target_color_bgr = (target_color[2], target_color[1], target_color[0])
    diff = np.abs(np.array(bgr_color, dtype=int) - np.array(target_color_bgr, dtype=int))
    return np.all(diff <= tolerance)

def open_egg():
    while True:
        if running_flag:
            pydirectinput.press('e')
        time.sleep(0.01)

def setup_gui():
    global gui
    gui = EggCounterGUI()
    gui.root.mainloop()

cls()
hatch_count = int(input("How many eggs do you open at once? "))
cls()
print('Auto-hatch by Justanother_game')
print('Macro running correctly')
print('To start press F2, to stop press F3')

def action_loop():
    global hatched_eggs, send_once, gui
    while True:
        if running_flag:
            if not detect_color(daily, daily_col, 10):
                pydirectinput.keyDown('E')
                pydirectinput.press('r')
                pydirectinput.keyUp('R')
                hatched_eggs += hatch_count
                send_once = True
                if gui:
                    try:
                        gui.egg_counter(hatched_eggs)
                    except:
                        pass
                time.sleep(0.1)
            else:
                if send_once:
                    print(f'Total eggs opened: {hatched_eggs}'.ljust(60), end="\r")
                    send_once = False
        else:
            time.sleep(0.3)

def toggle_switch(key):
    global running_flag
    if key == ON_switch:
        running_flag = not running_flag
        if running_flag:
            print("Script started".ljust(60))
            pydirectinput.keyDown('shift')
        else:
            print("\nScript paused".ljust(60))
            pydirectinput.keyUp('shift')
    elif key == OFF_switch:
        print(f"Script stopped".ljust(60), end="\r")
        elapsed_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(total_time.split(":"))))
        running_flag = False
        if elapsed_seconds >= 3600:
            message = (
                f"Hello!\n\n"
                f"You have been using this macro for {total_time} hour(s).\n\n"
                f"These macros take me a long time to make, so I'd be grateful if you left a tip :)"
            )
            result = ctypes.windll.user32.MessageBoxW(
                0,
                message,
                "Thank you!",
                0x1044
            )
            if result == 6:
                import webbrowser
                webbrowser.open("https://ko-fi.com/Youngblock2k/tip")
        sys.exit()

e_thread = threading.Thread(target=open_egg, daemon=True)
gui_thread = threading.Thread(target=setup_gui, daemon=True)
action_thread = threading.Thread(target=action_loop, daemon=True)
e_thread.start()
gui_thread.start()
action_thread.start()
with keyboard.Listener(on_press=toggle_switch) as listener:
    listener.join()
