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
import requests
import win32gui
import win32con
import win32api
import pygetwindow as gw
from pywinauto import Application

# DESCRIPTION: Faster egg hatching and egg counter with secret detection
# VERSIONS: all
version = "v28.2"

print = functools.partial(print, flush=True)

# global names
ON_switch = keyboard.Key.f2
OFF_switch = keyboard.Key.f3

running_flag = False    
total_time = ""
hatched_eggs = 0
daily_col = (238, 50, 94)
hatch_count = 0
secret_count = 0
multi = False
gui = None
webhook_link = None
webhook_user_id = None
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

if screen_width == 2560 and screen_height == 1440:
    center = (1280, 720)
    daily = (68, 695)
elif screen_width == 1920 and screen_height == 1080:
    center = (960, 540)
    daily = (59, 514) 
elif screen_width in [1366, 1364] and screen_height == 768:
    center = (683, 384)
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
        self.root.geometry("260x90+0+0")
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

        self.labels_frame = tk.Frame(
            self.main_frame,
            bg='#F5F5DC'
        )
        self.labels_frame.pack(side='left', fill='both', expand=True, padx=10, pady=5)

        self.egg_label = tk.Label(
            self.labels_frame, 
            text="Eggs Hatched: 0", 
            font=("Arial", 12, "bold"),
            bg='#F5F5DC', 
            fg='#8B4513',
            anchor='w'
        )
        self.egg_label.pack(fill='x', pady=(5, 2))

        self.secret_label = tk.Label(
            self.labels_frame, 
            text="Secrets Hatched: 0", 
            font=("Arial", 12, "bold"),
            bg='#F5F5DC', 
            fg='#8B4513',
            anchor='w'
        )
        self.secret_label.pack(fill='x', pady=(2, 5))

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
        self.labels_frame.bind('<Button-1>', self.s_drag)
        self.labels_frame.bind('<B1-Motion>', self.drag)
        self.egg_label.bind('<Button-1>', self.s_drag)
        self.egg_label.bind('<B1-Motion>', self.drag)
        self.secret_label.bind('<Button-1>', self.s_drag)
        self.secret_label.bind('<B1-Motion>', self.drag)
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
    
    def secret_counter(self, count):
        if self.root and self.secret_label:
            try:
                self.secret_label.config(text=f"Secrets Hatched: {count}")
                self.root.update_idletasks()
            except tk.TclError:
                pass
    
    def close(self, event):
        self.root.quit()
        sys.exit()

def auto_f11():
    rblx = [w for w in gw.getWindowsWithTitle('Roblox') if w.title == 'Roblox']
    if len(rblx) != 1:
        print("More than 1 roblox game running, please manually go into full screen" if rblx else "No Roblox window found")
        return

    hwnd = rblx[0]._hWnd
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    mon_rect = win32api.GetMonitorInfo(monitor)['Monitor']
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

    is_fullscreen = (
        left <= mon_rect[0] and top <= mon_rect[1] and
        right >= mon_rect[2] and bottom >= mon_rect[3] and
        not (style & (win32con.WS_CAPTION | win32con.WS_THICKFRAME))
    )

    if not is_fullscreen:
        win32gui.SetForegroundWindow(hwnd)
        Application().connect(handle=hwnd).window(handle=hwnd).type_keys('{F11}')
        print("Toggled fullscreen for Roblox")
    time.sleep(1.5)

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
            time.sleep(0.05)
            win32api.keybd_event(0x45, 0x12, 0, 0)
            win32api.keybd_event(0x45, 0x12, 2, 0)
        time.sleep(0.1)

def is_roblox_window(title):
    return title.strip() == "Roblox"

def get_rblx():
    roblox_windows = []
    def enum_window_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if is_roblox_window(title):
                roblox_windows.append(hwnd)

    win32gui.EnumWindows(enum_window_callback, None)
    return roblox_windows

def switch():
    roblox_windows = get_rblx()
    if not roblox_windows:
        print("No Roblox windows found")
        return
    while True:
        for hwnd in roblox_windows:
            if not running_flag:
                time.sleep(0.3)
                return
            try:
                win32gui.SetForegroundWindow(hwnd)                
                time.sleep(0.05)
                win32api.keybd_event(0x45, 0x12, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(0x45, 0x12, 2, 0)
            except Exception as e:
                continue

def setup_gui():
    global gui
    gui = EggCounterGUI()
    gui.root.mainloop()

webhook_path = os.path.join(os.path.expanduser("~"), "MacroClient", "Files", "webhook.txt")
def load_webhook():
    global webhook_link
    if os.path.exists(webhook_path):
        try:
            with open(webhook_path, "r") as file:
                webhook_link = file.read().strip()
        except Exception as e:
            print(f"Failed to load webhook: {e}")
    else:
        print(f"Webhook file not found at: {webhook_path}")

def notif():
    global webhook_user_id
    if webhook_link:
        user_id = input("Enter your Discord user ID (or type 0 if you don't want to get notified about hatches): ").strip()
        if user_id.isdigit():
            webhook_user_id = user_id if user_id != "0" else None

def secret_detect(coords, tolerance=10):
    screenshot = ImageGrab.grab()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    bgr_color = img[coords[1], coords[0]]
    diff = np.abs(np.array(bgr_color, dtype=int) - np.array((255, 255, 255), dtype=int))
    return np.all(diff <= tolerance)

def ss_webhook(webhook_url, ss_path):
    global hatched_eggs
    try:
        with open(ss_path, 'rb') as file:
            data = {}
            if webhook_user_id:
                data["content"] = f"[FASTHATCH {version}] <@{webhook_user_id}>\nSecret pet hatched after {hatched_eggs} eggs\nTotal: {secret_count}"
            else:
                data["content"] = f"[FASTHATCH {version}]\nSecret pet hatched after {hatched_eggs} eggs\nTotal: {secret_count}"

            response = requests.post(
                webhook_url,
                files={"file": ("FastHatchSecret.png", file)},
                data=data
            )
        if response.status_code == 200:
            os.remove(ss_path)
        return response.status_code
    except Exception as e:
        print(f"An error occurred while sending the screenshot: {e}")
        return None

def get_secret():
    global webhook_link, secret_count, gui
    while True:
        if secret_detect((center[0], 20)):
            if (secret_detect((center[0], 20)) and # top
                secret_detect((center[0], center[1])) and # mid
                secret_detect((100, center[1])) and # left
                secret_detect((center[0], (center[1] * 2 - 30)))): # bottom
                secret_count += 1
                if gui:
                    try:
                        gui.secret_counter(secret_count)
                    except:
                        pass
                time.sleep(3)

                screenshot = ImageGrab.grab()
                ss_path = os.path.join(os.getcwd(), "FastHatchSecret.png")
                screenshot.save(ss_path)
                if webhook_link:
                    status = ss_webhook(webhook_link, ss_path)
                    if status != 200:
                        print("Failed to send the screenshot. Check the webhook URL and permissions.")
        time.sleep(0.2)

cls()
multi_acc = input("Do you want to use this macro on multiple accounts? (yes/no): ").strip().lower()
multi = multi_acc in ["yes", "y"]
if not multi:
    hatch_count = int(input("How many eggs do you open at once? "))
    cls()
    load_webhook()
    notif()
cls()

print(f'Fast Hatch {version} by Youngblock2k\nMacro running correctly\nTo start press F2, to stop press F3')
def action_loop():
    global hatched_eggs, gui, multi
    while True:
        if running_flag:
            if multi:
                switch()
            else:
                if not detect_color(daily, daily_col, 10):
                    hatched_eggs += hatch_count
                    if gui:
                        try:
                            gui.egg_counter(hatched_eggs)
                        except:
                            pass
                    pydirectinput.keyDown('shift')
                    pydirectinput.keyDown('l')
                    pydirectinput.keyUp('l')
                    pydirectinput.keyUp('shift')
                    time.sleep(0.05)
        else:
            time.sleep(0.3)

def toggle_switch(key):
    global running_flag
    if key == ON_switch:
        running_flag = not running_flag
        if running_flag:
            print("Script started".ljust(60))
            if not multi:
                auto_f11()
            pydirectinput.keyUp('shift')
        else:
            print("\nScript paused".ljust(60))
            pydirectinput.keyUp('shift')
    elif key == OFF_switch:
        print(f"Script stopped".ljust(60), end="\r")
        pydirectinput.keyUp('shift')
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
action_thread = threading.Thread(target=action_loop, daemon=True)
e_thread.start()
action_thread.start()
if not multi:
    gui_thread = threading.Thread(target=setup_gui, daemon=True)
    gui_thread.start()
    monitor_thread = threading.Thread(target=get_secret, daemon=True)
    monitor_thread.start()

with keyboard.Listener(on_press=toggle_switch) as listener:
    listener.join()
