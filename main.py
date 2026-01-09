import os
import sys
import threading
import subprocess
import requests
import hashlib
import dearpygui.dearpygui as dpg
import mysql.connector
from mysql.connector import Error
import uuid
import json

GITHUB_REPO_OWNER = "Youngblock3k"
GITHUB_REPO_NAME = "Macros"
GITHUB_API_CONTENTS = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents"

HOME_FOLDER = os.path.join(os.path.expanduser("~"), "MacroClient")
INSTALL_FOLDER = os.path.join(HOME_FOLDER, "2OP")
DEEPSAKE_FOLDER = os.path.join(HOME_FOLDER, "Files")
os.makedirs(INSTALL_FOLDER, exist_ok=True)
os.makedirs(DEEPSAKE_FOLDER, exist_ok=True)

XOR_KEY = 0x2345269FE
encrypted_config = "793e7249de22163a068d76166849dc605321009363572006d06f4d2118922c50331d9f6055210cd0634e271b9b2c573d04dc2e3e7249de2216271a9b70166849dc6f55311b9160532100dc2e3e7249de221622088d71433d1b9a200e724bba4d7a063abd43791258cc31167e63de2214724b9a6340330b9f71517053de2059330a8c6d167e63de2214724b8d71580d0a9f200e724bba6b533b2a9b704015059160553e3b916d40155bd061462641cc2b1a220c9320185849de2214701a8d6e6b240c8c6b522b369d6746264bc42240201c9b2e3e7249de2216211a925d42371b97644d0d009a675a26008a7b1668498a7041376383"

def decrypt_config(encrypted_hex: str, key: int) -> dict:
    key_bytes = key.to_bytes((key.bit_length() + 7) // 8, 'big')
    encrypted = bytes.fromhex(encrypted_hex)
    decrypted = bytearray()
    for i, b in enumerate(encrypted):
        decrypted.append(b ^ key_bytes[i % len(key_bytes)])
    return json.loads(decrypted.decode('utf-8'))

DB_CONFIG = decrypt_config(encrypted_config, XOR_KEY)

MACROS = {}
running_process = None
console_lines = []
verified = False
current_tab = "verification"

def get_hwid():
    try:
        mac = uuid.getnode()
        return ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]).upper()
    except:
        return "UNKNOWN_HWID"

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except:
        return "UNKNOWN_IP"

def log(text):
    print(text)
    console_lines.append(text)
    if len(console_lines) > 500:
        console_lines.pop(0)
    if dpg.does_item_exist("console_text"):
        dpg.set_value("console_text", "\n".join(console_lines))
        dpg.set_y_scroll("console_window", 1.0)

def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        log("DB Connection successful!")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            discord_id VARCHAR(32) PRIMARY KEY,
            username VARCHAR(64),
            verified BOOLEAN DEFAULT FALSE,
            premium BOOLEAN DEFAULT FALSE,
            expiry DATETIME DEFAULT NULL,
            hwid VARCHAR(64) DEFAULT NULL,
            ip VARCHAR(45) DEFAULT NULL,
            join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
    except Error as e:
        log(f"DB CONNECTION FAILED: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def verify_user(sender, app_data):
    discord_id = dpg.get_value("discord_id_input").strip()
    username_input = dpg.get_value("username_input").strip()

    if not discord_id or not username_input:
        dpg.set_value("verify_status", "Fill both fields")
        return

    if not discord_id.isdigit() or len(discord_id) != 18:
        dpg.set_value("verify_status", "Invalid ID (18 digits required)")
        return

    current_hwid = get_hwid()
    current_ip = get_public_ip()

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT username, verified, premium, expiry, hwid, ip FROM users WHERE discord_id = %s", (discord_id,))
        row = cursor.fetchone()
        if row:
            db_username, verified_db, premium, expiry, db_hwid, db_ip = row
            if username_input.lower() != db_username.lower():
                dpg.set_value("verify_status", "Wrong username")
                return
            if db_hwid and db_hwid != current_hwid:
                dpg.set_value("verify_status", "HWID mismatch - contact support")
                log("HWID mismatch detected!")
                return
            if premium and expiry:
                from datetime import datetime
                if datetime.now() > datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S"):
                    dpg.set_value("verify_status", "Premium expired")
                    return
            if verified_db:
                global verified
                verified = True
                if not db_hwid or not db_ip:
                    cursor.execute("UPDATE users SET hwid = %s, ip = %s WHERE discord_id = %s",
                                   (current_hwid, current_ip, discord_id))
                    conn.commit()
                dpg.set_value("verify_status", "VERIFIED SUCCESSFULLY")
                dpg.configure_item("verify_button", enabled=False)
                dpg.set_value("status_label", "Status: Verified")
                dpg.configure_item("status_label", color=[100, 255, 100])
                enable_tabs()
            else:
                dpg.set_value("verify_status", "Not verified in DB")
        else:
            dpg.set_value("verify_status", "ID not registered")
    except Error as e:
        log(f"DB Error: {e}")
        dpg.set_value("verify_status", "DB failed")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def download_file(url, path):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    except:
        log(f"Download failed")
        return False

def get_git_sha(filepath):
    try:
        with open(filepath, "rb") as f:
            content = f.read()
        header = f"blob {len(content)}\0".encode()
        return hashlib.sha1(header + content).hexdigest()
    except:
        return None

def refresh_macros():
    global MACROS
    try:
        data = requests.get(GITHUB_API_CONTENTS).json()
        MACROS.clear()
        for item in data:
            if item["type"] == "file" and item["name"].endswith(".py"):
                name = item["name"]
                display = name.replace(".py", "").replace("_", " ").title()
                version = "Unknown"
                local_path = os.path.join(INSTALL_FOLDER, name)
                if os.path.exists(local_path):
                    try:
                        with open(local_path, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.startswith("version ="):
                                    version = line.split("=")[1].strip().strip('"\'')
                                    break
                    except:
                        pass
                MACROS[f"{display} V{version}"] = name
        log("Macros refreshed")
    except:
        log("Failed to refresh macros")

def check_github():
    log("Checking updates...")
    try:
        data = requests.get(GITHUB_API_CONTENTS).json()
        updated = 0
        for item in data:
            if item["type"] == "file" and item["name"].endswith(".py"):
                name = item["name"]
                local_path = os.path.join(INSTALL_FOLDER, name)
                remote_sha = item["sha"]
                local_sha = get_git_sha(local_path) if os.path.exists(local_path) else None
                if local_sha != remote_sha:
                    log(f"Updating {name}...")
                    if download_file(item["download_url"], local_path):
                        updated += 1
                        log(f"Updated {name}")
        log("All up to date" if updated == 0 else f"Updated {updated} files")
    except:
        log("GitHub check failed")
    refresh_macros()
    if current_tab == "macros":
        rebuild_macro_list()

def start_macro(sender, app_data, user_data):
    global running_process
    filename = user_data
    path = os.path.join(INSTALL_FOLDER, filename)
    if not os.path.exists(path):
        log(f"Missing: {filename}")
        return
    log(f"Launching {filename}...")
    try:
        if sys.platform == "win32":
            subprocess.Popen(['start', 'cmd', '/k', 'python', path], cwd=INSTALL_FOLDER, shell=True)
        else:
            subprocess.Popen(['python3', path], cwd=INSTALL_FOLDER)
        log("Macro launched")
    except:
        log("Launch failed")

def open_folder():
    try:
        if sys.platform == "win32":
            os.startfile(INSTALL_FOLDER)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", INSTALL_FOLDER])
        else:
            subprocess.Popen(["xdg-open", INSTALL_FOLDER])
        log("Opened folder")
    except:
        log("Failed to open folder")

def rebuild_macro_list():
    if not dpg.does_item_exist("macro_list_group"):
        return
    dpg.delete_item("macro_list_group", children_only=True)
    for display, filename in MACROS.items():
        exists = os.path.exists(os.path.join(INSTALL_FOLDER, filename))
        with dpg.group(horizontal=True, parent="macro_list_group"):
            dpg.add_text(f"{'Available' if exists else 'Missing'} {display}", color=[200, 255, 200] if exists else [255, 150, 150])
            if exists:
                dpg.add_button(label="START", callback=start_macro, user_data=filename, width=120)

def enable_tabs():
    tabs = ["welcome", "macros", "settings", "social", "webhook", "updates", "credits"]
    for tab in tabs:
        dpg.configure_item(f"{tab}_tab", enabled=True)
    dpg.configure_item("verify_to_unlock_label", show=False)

def switch_tab(sender, app_data, user_data):
    global current_tab
    if not verified and user_data != "verification":
        log("Verify first")
        return
    current_tab = user_data
    dpg.delete_item("content_area", children_only=True)

    for t in ["verification","welcome","macros","settings","social","webhook","updates","credits"]:
        dpg.bind_item_theme(f"{t}_tab", "tab_normal")
    dpg.bind_item_theme(f"{user_data}_tab", "tab_active")

    if user_data == "verification":
        dpg.add_text("Discord Verification", parent="content_area", color=[100,200,255])
        dpg.add_spacer(height=10, parent="content_area")
        dpg.add_input_text(tag="discord_id_input", hint="Discord ID (18 digits)", width=400, parent="content_area")
        dpg.add_spacer(height=8, parent="content_area")
        dpg.add_input_text(tag="username_input", hint="Discord Username", width=400, parent="content_area")
        dpg.add_spacer(height=15, parent="content_area")
        dpg.add_button(label="Verify", tag="verify_button", callback=verify_user, width=400, height=45, parent="content_area")
        dpg.add_spacer(height=10, parent="content_area")
        dpg.add_text("Status: Not verified", tag="verify_status", parent="content_area", color=[255,150,150])

    elif user_data == "welcome":
        dpg.add_text("Welcome to 2OP Macro Client!", parent="content_area", color=[100,180,255])
        dpg.add_spacer(height=20, parent="content_area")
        dpg.add_text("All features unlocked\nUse the tabs above to navigate\nMacros tab to launch scripts", parent="content_area")

    elif user_data == "macros":
        dpg.add_text("Macro Library", parent="content_area", color=[100,200,255])
        dpg.add_spacer(height=8, parent="content_area")
        dpg.add_button(label="Refresh List", callback=lambda s,a: (refresh_macros(), rebuild_macro_list()), parent="content_area", width=200)
        dpg.add_spacer(height=8, parent="content_area")
        dpg.add_group(tag="macro_list_group", parent="content_area")
        rebuild_macro_list()

    elif user_data == "settings":
        dpg.add_text("Settings - Coming Soon", parent="content_area")

    elif user_data == "social":
        dpg.add_text("Social Links", parent="content_area")
        dpg.add_text("Discord: https://discord.gg/yourinvite", parent="content_area")

    elif user_data == "webhook":
        dpg.add_text("Discord Webhook", parent="content_area")
        dpg.add_input_text(hint="Webhook URL", parent="content_area")
        dpg.add_button(label="Save & Test", parent="content_area")

    elif user_data == "updates":
        dpg.add_text("Updates", parent="content_area")
        dpg.add_button(label="Check GitHub Now", callback=check_github, parent="content_area")

    elif user_data == "credits":
        dpg.add_text("Credits", parent="content_area")
        dpg.add_text("Youngblock2k - Developer\nCommunity - Support", parent="content_area")

def first_frame_callback():
    switch_tab(None, None, "verification")

def build_ui():
    dpg.create_context()

    with dpg.theme(tag="tab_normal"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [45, 25, 55])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [65, 35, 75])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [55, 30, 65])

    with dpg.theme(tag="tab_active"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [90, 40, 110])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [110, 50, 130])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [100, 45, 120])

    with dpg.theme(tag="dark_purple"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [15, 10, 22])
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, [20, 15, 30])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, [80, 35, 100])
            dpg.add_theme_color(dpg.mvThemeCol_Button, [50, 25, 65])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [70, 35, 85])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [60, 30, 75])
            dpg.add_theme_color(dpg.mvThemeCol_Text, [220, 200, 255])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, [45, 25, 60])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, [65, 35, 80])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, [75, 40, 90])
            dpg.add_theme_color(dpg.mvThemeCol_Header, [80, 35, 100])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, [100, 45, 120])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, [90, 40, 110])
            dpg.add_theme_color(dpg.mvThemeCol_Separator, [60, 30, 80])
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 12)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 15)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 12)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 8)

    with dpg.font_registry():
        with dpg.font("C:/Windows/Fonts/segoeuib.ttf", 23, default_font=True, tag="bold_font"):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    with dpg.window(tag="main", label="2OP Macro Client", no_resize=False):
        dpg.bind_theme("dark_purple")
        dpg.bind_font("bold_font")

        with dpg.group(horizontal=True):
            with dpg.child_window(width=360, border=False):
                dpg.add_text("2OP Macro Manager", color=[160, 100, 220])
                dpg.add_spacer(height=20)
                dpg.add_button(label="Check GitHub Now", callback=check_github, width=-1, height=50)
                dpg.add_spacer(height=8)
                dpg.add_button(label="Open Install Folder", callback=open_folder, width=-1, height=50)
                dpg.add_spacer(height=40)
                dpg.add_text("Status: Not Verified", color=[255,120,160], tag="status_label")
                dpg.add_spacer(height=40)
                dpg.add_text("Available Scripts", color=[200,160,255], tag="available_scripts_label")
                dpg.add_text("(Verify to unlock)", color=[160,120,200], tag="verify_to_unlock_label")

            with dpg.child_window(border=False):
                with dpg.group(horizontal=True):
                    tabs = ["Verification","Welcome","Macros","Settings","Social","Webhook","Updates","Credits"]
                    for tab in tabs:
                        low = tab.lower()
                        btn = dpg.add_button(label=tab, height=50, tag=f"{low}_tab")
                        dpg.bind_item_theme(btn, "tab_normal")
                        dpg.configure_item(btn, callback=switch_tab, user_data=low)
                        dpg.configure_item(btn, enabled=(low == "verification"))

                dpg.add_spacer(height=12)
                dpg.add_separator()
                dpg.add_spacer(height=12)

                with dpg.child_window(tag="content_area", height=-230):
                    pass

                dpg.add_spacer(height=12)
                dpg.add_text("Console / Activity", color=[160, 100, 220])
                with dpg.child_window(height=210, tag="console_window"):
                    dpg.add_text("", tag="console_text")

    dpg.create_viewport(title="2OP Macro Client", width=1280, height=820, resizable=True, min_width=1000, min_height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main", True)

    dpg.bind_item_theme("verification_tab", "tab_active")
    dpg.set_frame_callback(1, first_frame_callback)

    init_db()
    threading.Thread(target=check_github, daemon=True).start()

    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    try:
        import socket
        s = socket.socket()
        s.bind(('127.0.0.1', 47200))
        s.close()
    except:
        print("Already running!")
        sys.exit(1)
    build_ui()