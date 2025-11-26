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
import requests
import keyboard as kb
import pygetwindow as gw
import win32gui, win32con, win32api
from pywinauto import Application
# DESCRIPTION: Plays the board game minigame and gets inf elixirs/special eggs
# VERSIONS: all

version = "15.1"

try:
    from ahk import AHK
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    bundled_ahk = os.path.join(base_path, 'AutoHotkey.exe')
    installed_ahk = r"C:\Program Files\AutoHotkey\AutoHotkey.exe"

    ahk_exe_path = bundled_ahk if os.path.exists(bundled_ahk) else installed_ahk
    ahk = AHK(executable_path=ahk_exe_path)
except Exception as e:
    ctypes.windll.user32.MessageBoxW(
        0,
        f"AutoHotkey could not be loaded from either bundled or installed path.\n\nError: {e}",
        "AutoHotkey Error",
        0x10
    )
    sys.exit()

res_info = 0
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)
if screen_width == 2560 and screen_height == 1440:
    res_info = 2560
    # dice
    dice = (1132, 1346)
    giant_dice = (1276, 1316)
    golden_dice = (1424, 1311)

    # main dice menu
    roll = dice
    change_dice = (1414, 1321)
    exit = (1543, 1320)

    # skip animation
    skip1 = (1214, 915)
    skip1_col = (124, 243, 19)
    skip2 = (1200, 817)
    skip2_col = (116, 241, 21)
    skip3 = (1219, 1019)
    skip3_col = (113, 241, 21)

    # detect the turn
    gui = (1431, 1346)
    gui_color = (164, 44, 18)
    dice_menu = (1649, 1282)
    dice_menu_col = (28, 166, 233)
    auto_roll = (1213, 1327)
    auto_roll_col = (216, 36, 74)

    # hatching icons
    arrow_up = (1710, 431)
    teleport = (1277, 1369)
    cam_pos = (1148, 631)
    cam_pos_col = (220, 60, 66)
    cam_pos_col2 = (197, 29, 29)
    daily = (68, 697)
    daily_col = (238, 50, 94)

    # blowing bubbles
    bubble_full = (1318, 737)
    bubble_full_col = (119, 242, 20)

    dice_regions = [
        ((922, 80), (1031, 200)),
        ((1043, 80), (1152, 200)),
        ((1166, 80), (1268, 200)),
        ((1283, 80), (1387, 200)),
        ((1402, 80), (1512, 200)),
        ((1526, 80), (1633, 200))
    ]

    giant_dice_regions = [
        ((686, 80), (788, 200)),
        ((805, 80), (910, 200)),
        ((927, 80), (1031, 200)),
        ((1046, 80), (1152, 200)),
        ((1167, 80), (1273, 200)),
        ((1282, 80), (1391, 200)),
        ((1403, 80), (1512, 200)),
        ((1524, 80), (1631, 200)),
        ((1647, 80), (1752, 200)),
        ((1764, 80), (1875, 200))
    ]
    points = [
        (708, 106), (829, 99), (928, 109), (1050, 118), (1168, 109),
        (1289, 103), (1410, 110), (1528, 108), (1649, 111), (1767, 114)
    ]
    points_gold = [(1231, 117)]

elif screen_width == 1920 and screen_height == 1080:
    res_info = 1920
    # dice
    dice = (825, 990)
    giant_dice = (957, 974)
    golden_dice = (1085, 973)

    # main dice menu
    roll = dice
    change_dice = golden_dice
    exit = (1192, 976)

    # skip animation
    skip1 = (911, 714)
    skip1_col = (113, 241, 21)
    skip2 = (903, 800)
    skip2_col = (118, 242, 20)
    skip3 = (890, 622)
    skip3_col = (125, 243, 19)

    # detect the turn
    gui = (1096, 998)
    gui_color = (164, 44, 18)
    dice_menu = (1287, 941)
    dice_menu_col = (28, 166, 233)
    auto_roll = (901, 980)
    auto_roll_col = (216, 36, 74)

    # hatching icons
    arrow_up = (1339, 286)
    teleport = (966, 1017)
    cam_pos = (859, 502)
    cam_pos_col = (236, 70, 76)
    cam_pos_col2 = (228, 44, 44)
    daily = (59, 513)
    daily_col = (238, 50, 94)

    # blowing bubbles
    bubble_full = (998, 556)
    bubble_full_col = (113, 241, 21)

    dice_regions = [
        ((662, 55), (725, 180)),
        ((765, 55), (839, 180)),
        ((871, 55), (940, 180)),
        ((978, 55), (1046, 180)),
        ((1081, 55), (1151, 180)),
        ((1187, 55), (1257, 180))
    ]

    giant_dice_regions = [
        ((439, 55), (528, 180)),
        ((544, 55), (636, 180)),
        ((650, 55), (742, 180)),
        ((751, 55), (844, 180)),
        ((857, 55), (950, 180)),
        ((964, 55), (1060, 180)),
        ((1068, 55), (1161, 180)),
        ((1178, 55), (1266, 180)),
        ((1277, 55), (1374, 180)),
        ((1383, 55), (1476, 180))
    ]

    points = [
        (444, 101), (546, 97), (661, 107), (765, 107), (869, 107), (976, 107), (1082, 107), (1187, 107), (1301, 102), (1396, 107)
    ]
    points_gold = [(919, 101)]
    
elif screen_width == 1366 and screen_height == 768:
    res_info = 1366
    # dice
    dice = (572, 686) #
    giant_dice = (683, 682) #
    golden_dice = (784, 686)

    # main dice menu
    roll = dice #
    change_dice = golden_dice #
    exit = (937, 660) #

    # skip animation
    skip1 = (639, 516) #
    skip1_col = (127, 243, 18) #
    skip2 = (623, 452) #
    skip2_col = (107, 240, 23) #
    skip3 = (890, 622)
    skip3_col = (125, 243, 19)

    # detect the turn
    gui = (789, 701) #
    gui_color = (164, 44, 18) #
    dice_menu = (936, 660) #
    dice_menu_col = (28, 166, 233) #
    auto_roll = (640, 690) #
    auto_roll_col = (217, 36, 74) #

    # hatching icons
    arrow_up = (978, 184) #
    teleport = (686, 716) #
    cam_pos = (611, 341) #
    cam_pos_col = (213, 61, 67) #
    cam_pos_col2 = (197, 29, 29) #
    daily = (47, 363) #
    daily_col = (238, 49, 94) #

    # blowing bubbles
    bubble_full = (711, 395) #
    bubble_full_col = (119, 242, 20) #

    dice_regions = [
        ((453, 69), (506, 128)),
        ((533, 69), (587, 128)),
        ((614, 69), (669, 128)),
        ((696, 69), (751, 128)),
        ((777, 69), (833, 128)),
        ((859, 69), (914, 128))
    ] #

    giant_dice_regions = [
        ((288, 69), (343, 128)),
        ((368, 69), (424, 128)),
        ((453, 69), (506, 128)),
        ((533, 69), (587, 128)),
        ((614, 69), (669, 128)),
        ((696, 69), (751, 128)),
        ((777, 69), (833, 128)),
        ((859, 69), (914, 128)),
        ((940, 69), (995, 128)),
        ((1021, 69), (1077, 128))
    ] #
    points = [
         (296, 82), (378, 82), (459, 82), (542, 82), (623, 81),
         (704, 83), (785, 82), (868, 81), (949, 81), (1023, 83)
    ] #
    points_gold = [(650, 77)] #
else:
    ctypes.windll.user32.MessageBoxW(
        0,
        f"Please either use 2560x1440, 1920x1080 or 1366x768 resolution and set your scale to 100% for this macro to work.\nCurrent resolution: {screen_width}x{screen_height}",
        "Invalid resolution",
        0x10
    )
    sys.exit()

print = functools.partial(print, flush=True)

# global names
TIME_switch = keyboard.Key.f1
ON_switch = keyboard.Key.f2
OFF_switch = keyboard.Key.f3
DEBUG_switch = keyboard.Key.f5

# others
running_flag = False
total_time = ""
items = []
flag_dice = False
flag_giant_dice = False
flag_golden_dice = False
risk_factor = 4
items_tile = 0
dice_count = 0
giant_dice_count = 0
golden_dice_count = 0
current_dice_type = None
temp_skip = False
send_once = True
hatch_count = 6
hatched_eggs = 0
fast_hatch_thread = None
webhook = False
temp_disable = False

def find_item(items, dice_type):
    global item_path
    regions = dice_regions if dice_type == 'dice' else giant_dice_regions
    screenshot = ImageGrab.grab()
    screen_np = np.array(screenshot)
    screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

    for item_path in items:
        template = cv2.imread(item_path)
        if template is None:
            print(f"WARNING: no images found: {item_path}")
            continue

        for slot, ((x1, y1), (x2, y2)) in enumerate(regions):
            region = screen_bgr[y1:y2, x1:x2]
            if region.shape[0] == 0 or region.shape[1] == 0:
                continue

            res = cv2.matchTemplate(region, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val >= 0.9:
                return (item_path, slot + 1)

    return ("None", 11)

def auto_f11():
    rblx = [w for w in gw.getWindowsWithTitle('Roblox') if w.title == 'Roblox']
    if len(rblx) != 1:
        print("More than 1 roblox game running" if rblx else "No Roblox window found")
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

def prompts():
    global dice_count, giant_dice_count, golden_dice_count, items, Hatching, name, hatch_count, risk_factor
    if res_info == 2560:
        item_options = {
            '1': 'elixir.png',
            '2': 'special_egg.png'
        }
    elif res_info == 1920:
        item_options2 = {
            '1': 'elixir2.png',
            '2': 'special_egg2.png'
        }
    elif res_info == 1366:
        item_options3 = {
            '1': 'elixir3.png',
            '2': 'special_egg3.png'
        }

    print("Which items do you want to farm?")
    print("  1. Infinite Elixirs")
    print("  2. Special Egg")
    print("For multiple options use commas (example: 1,2)")

    selected = input("Items to farm: ").replace(" ", "").split(",")
    if res_info == 2560:
        if selected == [''] or not selected:
            items = ['elixir.png']
            cls()
        else:
            if not [item_options.get(ans) for ans in selected if ans in item_options]:
                items = ['elixir.png']
                cls()
            else:
                items = [item_options.get(ans) for ans in selected]
    elif res_info == 1920:
        if selected == [''] or not selected:
            items = ['elixir2.png']
            cls()
        else:
            if not [item_options2.get(ans) for ans in selected if ans in item_options2]:
                items = ['elixir2.png']
                cls()
            else:
                items = [item_options2.get(ans) for ans in selected]
    elif res_info == 1366:
        if selected == [''] or not selected:
            items = ['elixir3.png']
            cls()
        else:
            if not [item_options3.get(ans) for ans in selected if ans in item_options3]:
                items = ['elixir3.png']
                cls()
            else:
                items = [item_options3.get(ans) for ans in selected]

    cls()
    dice_input = input("Enter how many normal dice do you have: ")
    giant_input = input("Enter how many giant dice do you have: ")
    golden_input = input("Enter how many golden dice do you have: ")

    try:
        dice_count = int(dice_input) if dice_input else 100
        giant_dice_count = int(giant_input) if giant_input else 100
        golden_dice_count = int(golden_input) if golden_input else 100
    except ValueError:
        dice_count = giant_dice_count = golden_dice_count = 0
    else:
        print(f"Normal Dice: {dice_count}, Giant Dice: {giant_dice_count}, Golden Dice: {golden_dice_count}")
        cls()

    cls()
    print("What egg do you want to hatch once your dice finishes (leave blank to blow bubbles):")
    egg_options = {
        '1': 'Infinity Egg',
        '2': 'Chance Egg',
        '3': 'Common Egg',
        '4': 'Hell Egg',
        '5': 'Void Egg',
        '6': 'Nightmare Egg',
        '7': 'Rainbow Egg',
        '8': 'Cyber Egg',
        '9': 'Neon Egg',
        '10': 'Carnival world egg (if an event is present)'
    }

    hatch_eggs = dict(egg_options.items())
    for key, name in hatch_eggs.items():
        print(f"  {key}. {name}")

    print('Leave blank to blow bubbles instead')
    hatch_input = input("Egg to hatch: ").strip()
    if hatch_input in hatch_eggs:
        Hatching = int(hatch_input)
    else:
        Hatching = 0
        print('Blowing bubbles instead of hatching')
        cls()

    if Hatching > 0:
        cls()
        try:
            hatch_count = int(input("How many eggs do you open at once? ") or 6)
        except ValueError:
            hatch_count = 6

    cls()
    print('Lower risk = less golden dice used BUT less items collected\nHigher risk = more golden dice used BUT more items collected\nThe suggested risk is 2\n')
    try:
        risk_input = input("How big of a risk do you want to take (default is 2)? ") or "2"
        risk_value = int(risk_input)
        if 0 <= risk_value <= 5:
            risk_factor = risk_value
        else:
            print("Invalid risk, using default risk of 2.")
            risk_factor = 2
    except ValueError:
        print("Invalid risk, using default risk of 2.")
        risk_factor = 2

    time.sleep(1)
    cls()
    print('Auto Board Game by Lisek_guy2')
    print('')
    print("Macro running correctly")
    print("To start press F2, to stop press F3")
    print('')


def format_time_ignore(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def update_session_time_ignore():
    global total_time
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        total_time = format_time_ignore(elapsed_time)
        time.sleep(1)


# Start the session time update thread
session_time_thread = threading.Thread(
    target=update_session_time_ignore, daemon=True)
session_time_thread.start()

# clearing the cmd
def cls():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def move(target_x, target_y):
    ahk.mouse_move(target_x, target_y)
    pydirectinput.click(target_x, target_y)


def nomove(x, y):
    ahk.mouse_move(x, y)

def detect_color(coords, target_color, tolerance=20):
    screenshot = ImageGrab.grab()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    bgr_color = img[coords[1], coords[0]]
    target_color_bgr = (target_color[2], target_color[1], target_color[0])
    diff = np.abs(np.array(bgr_color, dtype=int) - np.array(target_color_bgr, dtype=int))
    return np.all(diff <= tolerance)


def used_dice():
    cls()
    save_msg(f"Estimated tiles landed on: {items_tile}")
    save_msg(f"Dice left: {dice_count}")
    save_msg(f"Giant Dice left: {giant_dice_count}")
    save_msg(f"Golden Dice left: {golden_dice_count}")


def switch_dice(new_type):
    global current_dice_type
    if current_dice_type != new_type:
        while not detect_color(gui, gui_color):
            skip()
            time.sleep(0.1)
        move(change_dice[0], change_dice[1] + 10)
        if new_type == 'giant':
            move(*giant_dice)
        elif new_type == 'normal':
            move(*dice)
        elif new_type == 'golden':
            move(*golden_dice)
        current_dice_type = new_type
        save_msg(f"Switched to {new_type} dice")


def skip():
    if detect_color(skip1, skip1_col, 10):
        move(*skip1)
    elif detect_color(skip2, skip2_col, 10):
        move(*skip2)
    elif detect_color(skip3, skip3_col, 10):
        move(*skip3)

def fast_hatch():
    while running_flag:
        try:
            pydirectinput.press('r')
            time.sleep(0.4)
        except Exception as e:
            save_msg(f"ERROR: {e}")
            time.sleep(1)

def hatching_eggs():
    global hatch_count, send_once, hatched_eggs, fast_hatch_thread
    max_attempts = 20
    attempt = 0
    if Hatching == 0:
        save_msg('Used up all dice, blowing bubbles')
        time.sleep(0.3)
        pydirectinput.keyDown('w')
        time.sleep(0.3)
        pydirectinput.keyUp('w')
        move(*skip1)
        time.sleep(0.3)
        pydirectinput.mouseDown()
        anti_afk = 0
        while True:
            if detect_color(bubble_full, bubble_full_col):
                time.sleep(0.3)
                save_msg('No infinite backpack equipped, selling bubbles')
                move(*bubble_full)
                pydirectinput.click()
                time.sleep(4)
            else:
                time.sleep(1)
                anti_afk += 1
                if anti_afk == 180:
                    pydirectinput.press('space')
                    anti_afk = 0
                pydirectinput.mouseDown()

    else:
        while attempt < max_attempts:
            pydirectinput.press('esc')
            time.sleep(0.25)
            pydirectinput.press('r')
            time.sleep(0.25)
            pydirectinput.press('enter')
            time.sleep(4)
            save_msg('Camera position reset')

            pydirectinput.press('m')
            pydirectinput.keyDown('o')
            time.sleep(1.5)
            move(*teleport)
            time.sleep(2.5)
            pydirectinput.keyUp('o')
            save_msg('Setting the correct camera position')

            if detect_color(cam_pos, cam_pos_col, 25) or detect_color(cam_pos, cam_pos_col2, 25):
                w = 'w'
                a = 'a'
                s = 's'
                d = 'd'
                save_msg('Correct Color Found')
                break
            else:
                save_msg('Wrong camera position, retrying')
                attempt += 1

        if Hatching == 1:
            pydirectinput.keyDown(d)
            time.sleep(0.130)
            pydirectinput.keyUp(d)
            pydirectinput.keyDown(w)
            time.sleep(2.921)
            pydirectinput.keyUp(w)
            save_msg('Hatching the Infinity Egg')

        if Hatching == 2:
            pydirectinput.press('m')
            time.sleep(1.5)
            nomove(*arrow_up)
            for _ in range(6):
                pydirectinput.click()
                time.sleep(0.2)
            move(*teleport)
            time.sleep(2.5)
            pydirectinput.keyDown(w)
            time.sleep(1.688)
            pydirectinput.keyUp(w)
            pydirectinput.keyDown(a)
            time.sleep(0.631)
            pydirectinput.keyUp(a)
            pydirectinput.keyDown(w)
            time.sleep(1.718)
            pydirectinput.keyUp(w)
            pydirectinput.keyDown(d)
            time.sleep(0.668)
            pydirectinput.keyUp(d)
            pydirectinput.keyDown(w)
            time.sleep(0.851)
            pydirectinput.keyUp(w)
            save_msg('Hatching the Chance Egg')

        if Hatching == 3:
            pydirectinput.keyDown(d)
            time.sleep(0.112)
            pydirectinput.keyUp(d)
            pydirectinput.keyDown(w)
            time.sleep(2.414)
            pydirectinput.keyUp(w)
            pydirectinput.keyDown(a)
            time.sleep(0.808)
            pydirectinput.keyUp(a)
            save_msg('Hatching the Common Egg')

        if 9 > Hatching >= 4:
            pydirectinput.keyDown(d)
            time.sleep(0.080)
            pydirectinput.keyUp(d)
            pydirectinput.keyDown(w)
            time.sleep(2.312)
            pydirectinput.keyUp(w)
            pydirectinput.keyDown(d)
            time.sleep(0.213)
            pydirectinput.keyUp(d)
            pydirectinput.keyDown(w)
            time.sleep(1.414)
            pydirectinput.keyUp(w)
            time.sleep(0.5)
            if Hatching == 4:
                pydirectinput.keyDown(w)
                time.sleep(0.414)
                pydirectinput.keyUp(w)
                save_msg('Hatching the Hell Egg')

            if Hatching == 5:
                pydirectinput.keyDown(a)
                time.sleep(0.257)
                pydirectinput.keyUp(a)
                time.sleep(0.420)
                pydirectinput.keyDown(w)
                time.sleep(0.428)
                pydirectinput.keyUp(w)
                save_msg('Hatching the Void Egg')

            if Hatching == 6:
                pydirectinput.keyDown(d)
                time.sleep(0.151)
                pydirectinput.keyUp(d)
                time.sleep(0.471)
                pydirectinput.keyDown(w)
                time.sleep(0.301)
                pydirectinput.keyUp(w)
                save_msg('Hatching the Nightmare Egg')

            if Hatching == 7:
                pydirectinput.keyDown(d)
                time.sleep(0.453)
                pydirectinput.keyUp(d)
                pydirectinput.keyDown(w)
                time.sleep(0.215)
                pydirectinput.keyUp(w)
                save_msg('Hatching the Rainbow Egg')

            if Hatching == 8:
                pydirectinput.keyDown(d)
                time.sleep(0.225)
                pydirectinput.keyUp(d)
                pydirectinput.keyDown(s)
                time.sleep(0.953)
                pydirectinput.keyUp(s)
                pydirectinput.keyDown(d)
                time.sleep(0.453)
                pydirectinput.keyUp(d)
                save_msg('Hatching the Cyber Egg')

        if Hatching == 9:
            pydirectinput.press('m')
            time.sleep(1.5)
            nomove(*arrow_up)
            for _ in range(10):
                pydirectinput.click()
                time.sleep(0.2)
            move(*teleport)
            time.sleep(2.5)
            pydirectinput.keyDown(a)
            time.sleep(0.970)
            pydirectinput.keyUp(a)
            save_msg('Hatching the Neon Egg')

        if Hatching == 10:
            pydirectinput.keyDown(a)
            time.sleep(0.764)
            pydirectinput.keyUp(a)
            pydirectinput.keyDown(s)
            time.sleep(2.647)
            pydirectinput.keyUp(s)
            pydirectinput.keyDown(a)
            time.sleep(3.162)
            pydirectinput.keyUp(a)
            pydirectinput.keyDown(s)
            time.sleep(1.927)
            pydirectinput.keyUp(s)
            pydirectinput.keyDown(a)
            time.sleep(0.459)
            pydirectinput.keyUp(a)
            pydirectinput.keyDown(s)
            time.sleep(0.255)
            pydirectinput.keyUp(s)
            pydirectinput.keyDown(a)
            time.sleep(0.922)
            pydirectinput.keyUp(a)
            pydirectinput.keyDown(s)
            time.sleep(1.629)
            pydirectinput.keyUp(s)
            pydirectinput.keyDown(a)
            time.sleep(1.490)
            pydirectinput.keyUp(a)
            pydirectinput.keyDown(s)
            time.sleep(0.425)
            pydirectinput.keyUp(s)
            pydirectinput.keyDown(a)
            time.sleep(0.219)
            pydirectinput.keyUp(a)
            pydirectinput.keyDown(s)
            time.sleep(0.262)
            pydirectinput.keyUp(s)
            pydirectinput.keyDown(a)
            time.sleep(0.148)
            pydirectinput.keyUp(a)
            save_msg('Hatching the Carnival world egg')

        while running_flag:
            if fast_hatch_thread is None or not fast_hatch_thread.is_alive():
                fast_hatch_thread = threading.Thread(
                    target=fast_hatch, daemon=True)
                fast_hatch_thread.start()

            try:
                pydirectinput.keyDown('shift')
                if not detect_color(daily, daily_col):
                    pydirectinput.keyDown('l')
                    pydirectinput.keyUp('l')
                    hatched_eggs += hatch_count
                    send_once = True
                    time.sleep(0.1)
                elif send_once:
                    print(f'Total eggs opened: {hatched_eggs}'.ljust(60), end="\r")
                    send_once = False
            except Exception as e:
                save_msg(f"Error detected: {e}. Releasing shift")
                pydirectinput.keyUp('shift')
                time.sleep(1)
                continue
            finally:
                pass

        if fast_hatch_thread is not None:
            fast_hatch_thread.join()


def tolerance_temp(c1, c2, tolerance=5):
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

def check_dice(mode):
    global points
    target_color = (77, 220, 236)

    modes = {
        'normal': points[2:-2],
        'giant': points,
        'golden': points_gold
    }

    exclusions = {
        'normal': points[:2] + points[-2:],
        'giant': [],
        'golden': []
    }

    points_mode = modes.get(mode.lower())
    excluded = exclusions.get(mode.lower())

    if points_mode is None:
        raise ValueError(f"Invalid mode: {mode}")

    screenshot = ImageGrab.grab()
    pixels = screenshot.load()

    for x, y in points_mode:
        if not tolerance_temp(pixels[x, y], target_color):
            return False

    for x, y in excluded:
        if tolerance_temp(pixels[x, y], target_color):
            return False

    return True

log_queue = []
webhook_link = None
_lock = threading.Lock()
message_id = None

def webhook_link_batch():
    global message_id

    if not webhook_link:
        return

    if message_id is None:
        try:
            response = requests.post(webhook_link + "?wait=true", json={"content": "Starting..."})
            if response.status_code == 200:
                message_id = response.json()["id"]
            else:
                print(f"[Webhook] Failed to send initial message: {response.status_code} - {response.text}")
                return
        except Exception as e:
            print(f"[Webhook] Exception sending initial message: {e}")
            return

    while True:
        time.sleep(0.5)
        with _lock:
            if not log_queue or not any("Golden Dice left" in line for line in log_queue):
                continue


            batch_content = "\n".join(log_queue)
            log_queue.clear()
            batch = f"```text\n{batch_content}\n```"

        try:
            edit_url = f"{webhook_link}/messages/{message_id}"
            response = requests.patch(edit_url, json={"content": batch})
            if response.status_code not in [200, 204]:
                print(f"[Webhook] Failed to edit message: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[Webhook] Exception while editing message: {e}")

def save_msg(msg, type='print'):
    if type == 'print':
        print(msg)
    with _lock:
        log_queue.append(msg)
            

threading.Thread(target=webhook_link_batch, daemon=True).start()

def webhook_input():
    global webhook, webhook_link
    webhook_link_input = input("Enter your webhook: ").strip()
    if webhook_link_input:
        webhook_link = webhook_link_input
        webhook = True
        cls()
        print("Webhook enabled:", webhook_link)
        webhook_link_batch()
    else:
        print("Invalid webhook")

def noflood(name):
    save_msg('The dice didn\'t switch')
    while not detect_color(gui, gui_color, 5):
        skip()
        time.sleep(0.1)
    else:
        move(change_dice[0], change_dice[1] + 10)
        time.sleep(0.1)
        if name == 'giant':
            move(*giant_dice)
        if name == 'normal':
            move(*dice)
        save_msg('Dice switched after not being clicked')

def auto_roll_off():
    clicked = False
    while True:
        if running_flag:
            if detect_color(auto_roll, auto_roll_col, 30):
                if not clicked:
                    move(*auto_roll)
                    save_msg('Auto roll turned off')
                    clicked = True
                time.sleep(4)
                if giant_dice_count > 0:
                    move(*giant_dice)
                elif dice_count > 0:
                    move(*dice)
            else:
                clicked = False
                time.sleep(1)
        else:
            time.sleep(1)

threading.Thread(target=auto_roll_off, daemon=True).start()


cls()
print('Auto Board Game by Lisek_guy2')
print('')
start_time = time.time()
skips = False
prompts()

def action_loop():
    global dice_count, giant_dice_count, golden_dice_count
    global items_tile, running_flag, flag_dice, flag_giant_dice, flag_golden_dice, temp_skip

    while True:
        if not running_flag:
            time.sleep(0.1)
            continue
        flag_dice = dice_count > 0
        flag_giant_dice = giant_dice_count > 0
        flag_golden_dice = golden_dice_count > 0

        if not flag_dice and not flag_giant_dice:
            save_msg("No dice left :c")
            while not detect_color(gui, gui_color):
                skip()
                time.sleep(0.1)
            move(*exit)
            save_msg('', type='n')
            used_dice()
            hatching_eggs()
            return

        while detect_color(dice_menu, dice_menu_col):
            save_msg('No dice was selected, selecting it manually')
            move(*giant_dice)
        
        while not detect_color(gui, gui_color):
            skip()
            time.sleep(0.1)

        if not temp_skip:
            if flag_giant_dice:
                item_name, slot = find_item(items, 'giant')
                temp_skip = True
        if not flag_giant_dice:
            item_name, slot = find_item(items, 'dice')

        if slot == 11:
            save_msg("No items found.")
            if flag_giant_dice:
                switch_dice('giant')
                if not check_dice('giant'):
                    noflood('giant')
                item_name, slot = find_item(items, 'giant')
                if slot == 11:
                    move(*roll)
                    giant_dice_count -= 1
            elif flag_dice:
                switch_dice('normal')
                if not check_dice('normal'):
                    noflood('normal')
                time.sleep(0.1)
                move(*roll)
                dice_count -= 1
            used_dice()
            temp_skip = False
            continue
        save_msg(f"Found item '{item_name}' in slot {slot}")

        if slot == 10:
            if flag_giant_dice:
                switch_dice('giant')
                if not check_dice('giant'):
                    noflood('giant')
                move(*roll)
                giant_dice_count -= 1
            used_dice()
            temp_skip = False
            continue

        if 10 > slot > risk_factor:
            if flag_dice:
                switch_dice('normal')
                if not check_dice('normal'):
                    noflood('normal')
                time.sleep(0.1)
                move(*roll)
                dice_count -= 1
                used_dice()
                time.sleep(0.2)
                while not detect_color(gui, gui_color, 10):
                    skip()
                    time.sleep(0.1)
                temp_skip = True
                item_name, slot = find_item(items, 'dice')
                if slot == 11:
                    save_msg(f'DEBUG - rolling again')
                    move(*roll)
                    while not detect_color(gui, gui_color, 10):
                        skip()
                        time.sleep(0.1)
                    temp_skip = True
                    item_name, slot = find_item(items, 'dice')
                continue
            elif flag_giant_dice:
                switch_dice('giant')
                if not check_dice('giant'):
                    noflood('giant')
                move(*roll)
                giant_dice_count -= 1
                used_dice()
                continue
            else:
                save_msg("No dice to roll (if this error appears, good luck finding out what happened XD) :c")
                while not detect_color(gui, gui_color):
                    skip()
                    time.sleep(0.1)
                move(*exit)
                used_dice()
                hatching_eggs()
                return

        elif slot <= risk_factor:
            if golden_dice_count >= slot:
                switch_dice('golden')
                time.sleep(0.2)
                while slot > 0:
                    move(*roll)
                    golden_dice_count -= 1
                    slot -= 1
                    used_dice()
                    time.sleep(0.2)
                    while not detect_color(gui, gui_color):
                        skip()
                        time.sleep(0.1)
                items_tile += 1
                if flag_giant_dice:
                    switch_dice('giant')
                    while check_dice('golden'):
                        skip()
                        while not detect_color(gui, gui_color):
                            skip()
                            time.sleep(0.1)
                        move(change_dice[0], change_dice[1] + 10)
                        time.sleep(0.3)
                        move(*giant_dice)
                        save_msg(f"Switched to giant dice")
                    temp_skip = False
                    continue
                elif flag_dice:
                    switch_dice('normal')
                    time.sleep(0.1)
                    while check_dice('golden'):
                        skip()
                        while not detect_color(gui, gui_color):
                            skip()
                            time.sleep(0.1)
                        move(change_dice[0], change_dice[1] + 10)
                        time.sleep(0.3)
                        move(*giant_dice)
                        save_msg(f"Switched to giant dice")
                    temp_skip = False
                continue
            else:
                save_msg('Not enough Golden Dice to get items :c')
                while not detect_color(gui, gui_color):
                    skip()
                    time.sleep(0.1)
                move(*exit)
                used_dice()
                hatching_eggs()
                return

# on/off switch with f2 and f3 keys
def toggle_switch(key):
    global running_flag, total_time
    if key == ON_switch:
        running_flag = not running_flag
        if running_flag:
            print(f"Script started...".ljust(60), end="\r")
            auto_f11()
        if not running_flag:
            print(f"Script paused...".ljust(60), end="\r")
    elif key == OFF_switch:
        print(f"Script stopped".ljust(60), end="\r")
        running_flag = False
        elapsed_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(total_time.split(":"))))
        if elapsed_seconds >= 3600:
            pydirectinput.keyUp('w')
            pydirectinput.keyUp('a')
            pydirectinput.keyUp('s')
            pydirectinput.keyUp('d')
            pydirectinput.keyUp('shift')
            message = (
                f"Hello!\n\n"
                f"You have been using this macro for {total_time} hour(s).\n\n"
                f"These macros take me a long time to make, so I'd be grateful if you left a tip :)"
            )
            result = ctypes.windll.user32.MessageBoxW(
                0,
                message,
                "GUY2 MACROS",
                0x1044
            )
            if result == 6:
                import webbrowser
                webbrowser.open("https://ko-fi.com/lisek_guy2/tip")
        
        sys.exit()
    elif key == TIME_switch:
        print(f"Time elapsed: {total_time}")


with keyboard.Listener(on_press=toggle_switch) as listener:
    action_thread = threading.Thread(target=action_loop)
    action_thread.daemon = True
    action_thread.start()
    listener.join()
