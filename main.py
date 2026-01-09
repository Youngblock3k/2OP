import os
import sys
import time
import threading
import subprocess
import requests 
import hashlib
import shutil
import tkinter as tk
import webbrowser
import customtkinter as ctk 
from tkinter import messagebox
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
import random
import string





# ---------------- CONFIG ----------------
GITHUB_REPO_OWNER = "Youngblock3k"
GITHUB_REPO_NAME = "Macros"
GITHUB_API_CONTENTS = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents"
GITHUB_API_RELEASES = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases"

# Updated file paths
MACROCLIENT_FOLDER = os.path.join(os.path.expanduser("~"), "MacroClient")
INSTALL_FOLDER = os.path.join(MACROCLIENT_FOLDER, "2OP")
DEEPSAKE_FOLDER = os.path.join(MACROCLIENT_FOLDER, "Files")
SETTINGS_FILE = os.path.join(DEEPSAKE_FOLDER, "launcher_settings.json")
DURATION_FILE = os.path.join(DEEPSAKE_FOLDER, "duration.dat")
USERID_FILE = os.path.join(DEEPSAKE_FOLDER, "userid.dat")
WEBHOOK_FILE = os.path.join(DEEPSAKE_FOLDER, "webhook.txt")

# Create all necessary folders
os.makedirs(MACROCLIENT_FOLDER, exist_ok=True)
os.makedirs(INSTALL_FOLDER, exist_ok=True)
os.makedirs(DEEPSAKE_FOLDER, exist_ok=True)

# Create webhook.txt if it doesn't exist
if not os.path.exists(WEBHOOK_FILE):
    with open(WEBHOOK_FILE, 'w') as f:
        f.write("")

WINDOW_WIDTH = 920
WINDOW_HEIGHT = 640
SPLASH_SECONDS_MIN = 1

# --- Discord Configuration ---
DISCORD_SERVER_ID = "1381327215748321300" 
DISCORD_ROLE_ID_MEMBER = "1425231292986949632"
DISCORD_ROLE_ID_PREMIUM = "1430493309331312772"
DISCORD_VERIFICATION_CHANNEL_ID = "1425231371135094845"
# ----------------------------------------------------------------

# Single instance check
def is_app_already_running():
    """Check if another instance is already running"""
    import socket
    try:
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(('localhost', 47200))
        return False
    except socket.error:
        return True

if is_app_already_running():
    messagebox.showwarning("Already Running", "2OP Macro Client is already running!")
    sys.exit(1)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- CUSTOM STYLING CONFIG ---
GRAY_COLOR = "#343638"
BUTTON_FG_COLOR = GRAY_COLOR
BUTTON_HOVER_COLOR = "#444648"
BUTTON_FONT = ("Arial", 12, "bold")
WARNING_COLOR = "#e74c3c"
DISCORD_COLOR = "#5865F2" # Discord's brand color
DISCORD_HOVER = "#4c55db"
SUCCESS_COLOR = "#2ecc71"
# -----------------------------

# --- HELPER FUNCTIONS ---

def safe_request_json(url, timeout=12):
    """Safely performs a GET request and returns JSON."""
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Request failed for {url}: {e}")
        return None

def download_file(url, out_path, console_widget=None):
    """Downloads a file from a URL to a specified path. This function will overwrite the existing file."""
    try:
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        with open(out_path, "wb") as fh:
            for chunk in r.iter_content(8192):
                if chunk:
                    fh.write(chunk)
        return True
    except Exception as e:
        print(f"Download failed for {url}: {e}")
        return False

def _get_local_git_sha(filepath):
    """Calculates the SHA1 hash (hexdigest) of a local file's content."""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        text_content = content.decode('utf-8', errors='replace')
        normalized_content = text_content.replace('\r\n', '\n').replace('\r', '\n')
        normalized_bytes = normalized_content.encode('utf-8')

        # The Git SHA calculation for a blob includes a header: "blob <size>\x00"
        header = f"blob {len(normalized_bytes)}\x00".encode('utf-8')
        
        hasher = hashlib.sha1()
        hasher.update(header + normalized_bytes)
        
        return hasher.hexdigest()
    except Exception:
        return None

def log_console(widget, text):
    """Logs text to the console widget AND webhook.txt file."""
    ts = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{ts}] {text}\n"
    
    # Log to console widget
    if widget:
        try:
            widget.configure(state="normal")
            widget.insert("end", log_entry)
            widget.see("end")
            widget.configure(state="disabled")
        except Exception:
            pass
    
    # Log to webhook.txt file
    try:
        with open(WEBHOOK_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Failed to write to webhook.txt: {e}")
            
def get_current_ms():
    """Returns current time in milliseconds."""
    return int(time.time() * 1000)

def load_settings():
    """Loads persistent settings from JSON file."""
    default_settings = {
        "auto_update": True,
        "theme": "Dark",
        "resolution": "920x640",
        "access_tokens": {},
        "active_verification_id": None,
        "active_verification_username": None,
        "webhook_url": "",
        "webhook_enabled": False
    }
    
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                loaded = json.load(f)
                for key, value in default_settings.items():
                    if key not in loaded:
                        loaded[key] = value
                return loaded
    except Exception as e:
        print(f"Error loading settings: {e}")
    
    return default_settings

def save_settings(settings):
    """Saves settings to JSON file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def save_duration(duration_ms):
    """Saves duration to duration.dat file."""
    try:
        with open(DURATION_FILE, 'w') as f:
            f.write(str(duration_ms))
        return True
    except Exception as e:
        print(f"Error saving duration: {e}")
        return False

def load_duration():
    """Loads duration from duration.dat file."""
    try:
        if os.path.exists(DURATION_FILE):
            with open(DURATION_FILE, 'r') as f:
                return int(f.read().strip())
    except Exception:
        pass
    return 0

def save_userid(userid):
    """Saves user ID to userid.dat file."""
    try:
        with open(USERID_FILE, 'w') as f:
            f.write(userid)
        return True
    except Exception as e:
        print(f"Error saving userid: {e}")
        return False

def load_userid():
    """Loads user ID from userid.dat file."""
    try:
        if os.path.exists(USERID_FILE):
            with open(USERID_FILE, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return None

def get_macro_description(filepath):
    """Extracts description and version from macro file using tags."""
    description = "No description available."
    version = "Unknown version"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for description tags
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('# DESCRIPTION:'):
                description = line.replace('# DESCRIPTION:', '').strip()
            elif line.startswith('#DISCRIPTION:'):
                description = line.replace('#DISCRIPTION:', '').strip()
            elif line.startswith('version =') and '=' in line:
                # Extract version from version = "v28.2"
                version_part = line.split('=')[1].strip().strip('"\'')
                version = version_part
        
        # Fallback: look for version variable in code
        if version == "Unknown version":
            for line in content.split('\n'):
                if 'version' in line and '=' in line and not line.strip().startswith('#'):
                    try:
                        version_part = line.split('=')[1].strip().strip('"\'')
                        if version_part:
                            version = version_part
                            break
                    except:
                        pass
                        
    except Exception as e:
        print(f"Error reading macro info from {filepath}: {e}")
    
    return description, version

# --- DYNAMIC MACRO LIST (Used for Sidebar and Macro Details) ---
APP_MACROS = {
    "Auto-Hatch": {"color": BUTTON_FG_COLOR, "hover": BUTTON_HOVER_COLOR, "description": "Automates egg hatching with user-defined settings.", "filename": "Auto_Hatch.py", "version": "Unknown"},
    "Auto-Bubble": {"color": BUTTON_FG_COLOR, "hover": BUTTON_HOVER_COLOR, "description": "Experimental bubble collector utility.", "filename": "Auto_Bubble.py", "version": "Unknown"},
    "Auto-Fish": {"color": BUTTON_FG_COLOR, "hover": BUTTON_HOVER_COLOR, "description": "An advanced auto fishing macro designed for consistency.", "filename": "Auto_Fish.py", "version": "Unknown"}
}
# --------------------------

class LauncherApp(ctk.CTk):
    def __init__(self, auto_update=True):
        super().__init__()
        
        # Load persistent settings first
        self.settings = load_settings()
        self.auto_update_on_start = self.settings.get("auto_update", auto_update)
        self.access_tokens = self.settings.get("access_tokens", {})
        self.active_verification_id = self.settings.get("active_verification_id")
        self.active_verification_username = self.settings.get("active_verification_username")
        self.webhook_url = self.settings.get("webhook_url", "")
        self.webhook_enabled = self.settings.get("webhook_enabled", False)
        
        # Load from .dat files (backward compatibility)
        saved_duration = load_duration()
        saved_userid = load_userid()
        if saved_userid and not self.active_verification_id:
            self.active_verification_id = saved_userid
            if saved_duration > 0:
                self.access_tokens[saved_userid] = saved_duration
        
        # Apply saved theme and resolution
        saved_theme = self.settings.get("theme", "Dark")
        saved_resolution = self.settings.get("resolution", "920x640")
        ctk.set_appearance_mode(saved_theme)
        
        # Parse resolution
        try:
            width, height = map(int, saved_resolution.split('x'))
            self.geometry(f"{width}x{height}")
        except:
            self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        self.title("2OP Macro Client")
        self.minsize(840, 540)
        
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw//2)-(self.winfo_width()//2), (sh//2)-(self.winfo_height()//2)
        self.geometry(f"+{x}+{y}")

        self.repo_files = []
        self.local_files = {}
        self.proc = None
        self.proc_lock = threading.Lock()
        self.current_macro_name = None 
        self._is_macro_running = False 
        
        self.last_verification_status = True  # Always verified now
        self.macro_start_time = None 
        self.macro_timer_thread = None
        self.macro_runtime_var = tk.StringVar(value="00h 00m 00s")
        
        # Store pending verification data
        self.pending_verification = None
        
        # Webhook management
        self.webhook_active = False
        self.webhook_thread = None
        self.last_webhook_update = 0
        self.webhook_update_interval = 30  # seconds
        self.webhook_message_id = None
        
        self._refresh_app_macros_from_local_files()
        self._build_ui()
        
        # MOVE THE PROTOCOL BINDING HERE - AFTER UI IS BUILT
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # ADD THESE LINES FOR AUTO-SETUP:
        self.after(1000, self.install_required_packages)  # Install packages first
        self.after(2000, self.clean_corrupted_files)      # Clean corrupted files
        
        self.after(150, self._start_with_splash)
        self._start_sidebar_refresh_loop()
        
        # Start webhook monitoring if enabled
        if self.webhook_enabled and self.webhook_url:
            self.after(5000, self._start_webhook_monitoring)

    def install_required_packages(self):
        """Install required packages for macros if they're not installed"""
        required_packages = [
            'pyautogui',    # For mouse and keyboard automation
            'keyboard',     # For global hotkey detection
            'psutil',       # For process management
            'requests'      # For HTTP requests
        ]
        
        log_console(self.console, "📦 Checking required packages...")
        
        for package in required_packages:
            try:
                # Try to import the package
                __import__(package)
                log_console(self.console, f"✅ {package} is already installed")
            except ImportError:
                # Package not found, install it
                log_console(self.console, f"📥 Installing {package}...")
                try:
                    import subprocess
                    import sys
                    
                    # Use pip to install the package
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install', package, 
                        '--quiet', '--disable-pip-version-check'
                    ])
                    
                    log_console(self.console, f"✅ Successfully installed {package}")
                    
                except subprocess.CalledProcessError:
                    log_console(self.console, f"❌ Failed to install {package}")
                except Exception as e:
                    log_console(self.console, f"❌ Error installing {package}: {e}")

    def clean_corrupted_files(self):
        """Delete files that contain launcher code instead of macro code"""
        log_console(self.console, "🧹 Cleaning corrupted files...")
        
        deleted_count = 0
        for filename in os.listdir(INSTALL_FOLDER):
            if filename.endswith('.py'):
                filepath = os.path.join(INSTALL_FOLDER, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # If it contains launcher code, delete it
                    if 'LauncherApp' in content or 'ctk.CTk' in content:
                        os.remove(filepath)
                        log_console(self.console, f"🗑️ Deleted corrupted: {filename}")
                        deleted_count += 1
                        
                except Exception as e:
                    log_console(self.console, f"⚠️ Could not check {filename}: {e}")





        
        if deleted_count > 0:
            log_console(self.console, f"✅ Deleted {deleted_count} corrupted files")
        else:
            log_console(self.console, "✅ No corrupted files found")
        
        # Refresh the file list
        self._refresh_app_macros_from_local_files()
        self._trigger_sidebar_rebuild()

        
    def _save_current_settings(self):
        """Saves current state to settings file."""
        self.settings.update({
            "auto_update": self.auto_update_on_start,
            "theme": ctk.get_appearance_mode(),
            "resolution": f"{self.winfo_width()}x{self.winfo_height()}",
            "access_tokens": self.access_tokens,
            "active_verification_id": self.active_verification_id,
            "active_verification_username": self.active_verification_username,
            "webhook_url": self.webhook_url,
            "webhook_enabled": self.webhook_enabled
        })
        save_settings(self.settings)
        
        # Also save to .dat files for compatibility
        if self.active_verification_id:
            save_userid(self.active_verification_id)
            expiry_time = self.access_tokens.get(self.active_verification_id, 0)
            if expiry_time > 0:
                save_duration(expiry_time)

    # --- ACCESS CONTROL LOGIC ---
    def _is_verified(self):
        """ALWAYS RETURN TRUE - ALL MACROS ARE ALLOWED"""
        return True

    def _get_time_remaining(self):
        """ALWAYS RETURN VERIFIED STATUS"""
        return "Always Verified"

    # --- SIMPLE DISCORD BOT VERIFICATION SYSTEM ---
    def _show_discord_id_input(self):
        """COMING SOON - Verification disabled"""
        messagebox.showinfo("COMING SOON", "Discord verification feature is coming soon!\n\nAll macros are currently available without verification.")

    def _generate_verification_code(self, discord_id):
        """COMING SOON - Verification disabled"""
        messagebox.showinfo("COMING SOON", "Discord verification feature is coming soon!\n\nAll macros are currently available without verification.")

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Text copied to clipboard!")

    def _check_discord_verification(self, discord_id, verification_code):
        """COMING SOON - Verification disabled"""
        messagebox.showinfo("COMING SOON", "Discord verification feature is coming soon!\n\nAll macros are currently available without verification.")

    def _complete_verification(self, discord_id, username):
        """COMING SOON - Verification disabled"""
        messagebox.showinfo("COMING SOON", "Discord verification feature is coming soon!\n\nAll macros are currently available without verification.")

    # --- TIMER LOGIC ---
    def _start_macro_timer(self):
        """Starts the timer thread to track macro runtime."""
        if self.macro_timer_thread is None or not self.macro_timer_thread.is_alive():
            self.macro_start_time = time.time()
            self.macro_timer_thread = threading.Thread(target=self._run_macro_timer, daemon=True)
            self.macro_timer_thread.start()

    def _stop_macro_timer(self):
        """Stops the macro runtime timer."""
        self.macro_start_time = None
        self.macro_runtime_var.set("00h 00m 00s")

    def _run_macro_timer(self):
        """Thread function for updating the runtime display."""
        while self.macro_start_time is not None:
            elapsed_seconds = int(time.time() - self.macro_start_time)
            hours = elapsed_seconds // 3600
            minutes = (elapsed_seconds % 3600) // 60
            seconds = elapsed_seconds % 60
            
            runtime_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
            self.macro_runtime_var.set(runtime_str)
            
            # Update the UI every second
            time.sleep(1)

    # --- DYNAMIC MACRO/LOCAL FILE MANAGEMENT ---
    def _refresh_app_macros_from_local_files(self):
        """Scans the INSTALL_FOLDER for Python files, calculates their SHA and extracts descriptions."""
        global APP_MACROS
        
        self.local_files.clear()
        
        try:
            all_local_files = os.listdir(INSTALL_FOLDER)
        except Exception:
            all_local_files = []
            
        for filename in all_local_files:
            filepath = os.path.join(INSTALL_FOLDER, filename)
            
            if filename.endswith(".py"):
                self.local_files[filename] = _get_local_git_sha(filepath)
                
                # Update description and version from file content
                display_name = filename.replace(".py", "").replace("_", "-").title()
                description, version = get_macro_description(filepath)
                
                existing_key = None
                for key, data in APP_MACROS.items():
                    if data["filename"].lower() == filename.lower():
                        existing_key = key
                        break
                
                if existing_key is None:
                    # Dynamically add locally found scripts that aren't in the default list
                    APP_MACROS[display_name] = {
                        "color": BUTTON_FG_COLOR, 
                        "hover": BUTTON_HOVER_COLOR, 
                        "description": description, 
                        "filename": filename,
                        "version": version
                    }
                else:
                    # Update existing macro description and version
                    APP_MACROS[existing_key]["description"] = description
                    APP_MACROS[existing_key]["version"] = version
            else:
                 self.local_files[filename] = True 

    def _is_file_downloaded(self, filename):
        """Checks if a python script file exists locally AND has a calculated SHA."""
        local_sha = self.local_files.get(filename)
        return local_sha is not None and local_sha is not True
    
    def _get_orphaned_files(self):
        """Returns a list of local Python files that do not exist in the remote repo."""
        local_py_files = set(
            name for name, sha in self.local_files.items() 
            if name.endswith(".py") and sha is not True and sha is not None
        )
        remote_files = set(data['name'] for data in self.repo_files)
        return sorted(list(local_py_files - remote_files))

    def _start_sidebar_refresh_loop(self):
        """
        Updates the access status label text and checks for token expiry.
        """
        is_verified = self._is_verified()
        
        # Check if status has changed (e.g., just verified, or just expired)
        if is_verified != self.last_verification_status:
            self._trigger_sidebar_rebuild()
            self.last_verification_status = is_verified
        
        # Always update the timer display
        self._update_access_status_display(is_verified)
        
        self.after(1000, self._start_sidebar_refresh_loop)

    def _trigger_sidebar_rebuild(self):
        """A dedicated function to rebuild the dynamic macro list."""
        self._refresh_app_macros_from_local_files()
        self.after(0, self._build_ui_sidebar)
        
    # --- WEBHOOK FUNCTIONS ---
    def _start_webhook_monitoring(self):
        """Starts the webhook monitoring thread."""
        if self.webhook_url and self.webhook_enabled and not self.webhook_active:
            self.webhook_active = True
            self.webhook_thread = threading.Thread(target=self._webhook_monitor_loop, daemon=True)
            self.webhook_thread.start()
            log_console(self.console, "🔗 Webhook monitoring started")
            self._send_webhook_message("🟢 **2OP Macro Client Started**\nWebhook monitoring enabled!")

    def _stop_webhook_monitoring(self):
        """Stops the webhook monitoring."""
        if self.webhook_active:
            self.webhook_active = False
            log_console(self.console, "🔗 Webhook monitoring stopped")
            self._send_webhook_message("🔴 **2OP Macro Client Stopped**\nWebhook monitoring disabled!")

    def _webhook_monitor_loop(self):
        """Main webhook monitoring loop that updates the Discord embed."""
        while self.webhook_active:
            try:
                current_time = time.time()
                if current_time - self.last_webhook_update >= self.webhook_update_interval:
                    self._update_webhook_embed()
                    self.last_webhook_update = current_time
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                log_console(self.console, f"❌ Webhook monitor error: {e}")
                time.sleep(30)  # Wait longer on error

    def _update_webhook_embed(self):
        """Updates or creates the Discord webhook embed with current status."""
        if not self.webhook_url or not self.webhook_enabled:
            return

        try:
            # Get current console logs (last 10 lines)
            console_logs = self._get_recent_console_logs(10)
            
            # Get macro status
            macro_status = "No macro running"
            runtime = "00h 00m 00s"
            if self._is_macro_running and self.current_macro_name:
                elapsed_seconds = int(time.time() - self.macro_start_time) if self.macro_start_time else 0
                hours = elapsed_seconds // 3600
                minutes = (elapsed_seconds % 3600) // 60
                seconds = elapsed_seconds % 60
                runtime = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
                macro_status = f"🟢 **{self.current_macro_name}** - {runtime}"
            else:
                macro_status = "🔴 No macro running"
            
            # Get available macros count
            available_macros = sum(1 for data in APP_MACROS.values() if self._is_file_downloaded(data["filename"]))
            
            # Create embed
            embed = {
                "title": "🔧 2OP Macro Client - Live Status",
                "color": 0x00ff00 if self._is_macro_running else 0xff0000,
                "fields": [
                    {
                        "name": "📊 Client Status",
                        "value": f"**Macro Status:** {macro_status}\n"
                                f"**Runtime:** {runtime}\n"
                                f"**Available Macros:** {available_macros}\n"
                                f"**Last Update:** <t:{int(time.time())}:R>",
                        "inline": False
                    },
                    {
                        "name": "📝 Recent Activity",
                        "value": f"```{console_logs[-1000:]}```" if console_logs else "No recent activity",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "2OP Macro Client • Auto-updating every 30 seconds"
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            payload = {
                "embeds": [embed],
                "username": "2OP Macro Client",
                "avatar_url": "https://cdn.discordapp.com/attachments/1381327215748321300/1425231371135094845/2OP_Logo.png"
            }

            # Always send new message for simplicity (Discord webhooks don't support editing easily)
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code in [200, 204]:
                pass  # Success
            else:
                log_console(self.console, f"❌ Webhook send failed: {response.status_code}")

        except Exception as e:
            log_console(self.console, f"❌ Webhook update failed: {e}")

    def _send_webhook_message(self, message):
        """Sends a simple message to the webhook."""
        if not self.webhook_url or not self.webhook_enabled:
            return

        try:
            payload = {
                "content": message,
                "username": "2OP Macro Client",
                "avatar_url": "https://cdn.discordapp.com/attachments/1381327215748321300/1425231371135094845/2OP_Logo.png"
            }
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            log_console(self.console, f"❌ Webhook message failed: {e}")

    def _send_macro_start_webhook(self, macro_name):
        """Sends webhook notification when macro starts."""
        if not self.webhook_url or not self.webhook_enabled:
            return

        try:
            embed = {
                "title": "🚀 Macro Started",
                "description": f"**{macro_name}** has been started",
                "color": 0x00ff00,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "2OP Macro Client"
                }
            }
            payload = {
                "embeds": [embed],
                "username": "2OP Macro Client",
                "avatar_url": "https://cdn.discordapp.com/attachments/1381327215748321300/1425231371135094845/2OP_Logo.png"
            }
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            log_console(self.console, f"❌ Macro start webhook failed: {e}")

    def _send_macro_stop_webhook(self, macro_name, runtime):
        """Sends webhook notification when macro stops."""
        if not self.webhook_url or not self.webhook_enabled:
            return

        try:
            embed = {
                "title": "🛑 Macro Stopped",
                "description": f"**{macro_name}** has been stopped\n**Runtime:** {runtime}",
                "color": 0xff0000,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "2OP Macro Client"
                }
            }
            payload = {
                "embeds": [embed],
                "username": "2OP Macro Client",
                "avatar_url": "https://cdn.discordapp.com/attachments/1381327215748321300/1425231371135094845/2OP_Logo.png"
            }
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            log_console(self.console, f"❌ Macro stop webhook failed: {e}")

    def _get_recent_console_logs(self, line_count=10):
        """Gets recent console logs from webhook.txt"""
        try:
            if os.path.exists(WEBHOOK_FILE):
                with open(WEBHOOK_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                # Get last N lines
                recent_lines = lines[-line_count:] if len(lines) > line_count else lines
                return ''.join(recent_lines).strip()
            return "No log file found"
        except Exception as e:
            return f"Error reading logs: {e}"

    def _test_webhook(self):
        """Tests the webhook connection."""
        if not self.webhook_url:
            messagebox.showwarning("No Webhook", "Please enter a webhook URL first.")
            return

        try:
            test_embed = {
                "title": "🔧 2OP Macro Client - Test Message",
                "description": "This is a test message to verify your webhook is working correctly!",
                "color": 0x3498db,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "2OP Macro Client - Webhook Test"
                }
            }

            payload = {
                "embeds": [test_embed],
                "username": "2OP Macro Client",
                "avatar_url": "https://cdn.discordapp.com/attachments/1381327215748321300/1425231371135094845/2OP_Logo.png"
            }

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code in [200, 204]:
                messagebox.showinfo("Success", "✅ Webhook test successful! Check your Discord channel.")
                log_console(self.console, "✅ Webhook test successful")
            else:
                messagebox.showerror("Error", f"❌ Webhook test failed: {response.status_code}")
                log_console(self.console, f"❌ Webhook test failed: {response.status_code}")

        except Exception as e:
            messagebox.showerror("Error", f"❌ Webhook test failed: {e}")
            log_console(self.console, f"❌ Webhook test failed: {e}")

    def _save_webhook_settings(self):
        """Saves webhook settings and restarts monitoring."""
        self.webhook_url = self.webhook_url_entry.get().strip()
        self.webhook_enabled = self.webhook_enabled_var.get()
        
        self._save_current_settings()
        
        # Restart webhook monitoring if enabled
        if self.webhook_enabled and self.webhook_url:
            self._stop_webhook_monitoring()
            self.after(1000, self._start_webhook_monitoring)
            log_console(self.console, "✅ Webhook settings saved and monitoring started")
            messagebox.showinfo("Success", "✅ Webhook settings saved!\nLive updates will be sent to your Discord.")
        else:
            self._stop_webhook_monitoring()
            log_console(self.console, "✅ Webhook settings saved (monitoring disabled)")

    # --- UI & Startup ---
    def _start_with_splash(self):
        try:
            log_console(self.console, "Initializing client...")
            # Show loaded verification status
            if self._is_verified():
                log_console(self.console, f"Loaded verification for: {self.active_verification_username}")
        except Exception:
            pass

        def _after_splash():
            try:
                if getattr(self, 'auto_update_on_start', False):
                    log_console(self.console, "Auto-update enabled. Checking GitHub for new files...")
                    threading.Thread(target=self._manual_update_thread, daemon=True).start()
            except Exception:
                pass

        try:
            delay_ms = max(100, int(SPLASH_SECONDS_MIN * 1000))
            self.after(delay_ms, _after_splash)
        except Exception:
            _after_splash()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar (Column 0)
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=8)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(12,8), pady=12)
        self.sidebar.grid_propagate(False)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="2OP Macro Manager", font=("Arial", 18, "bold"))
        self.logo_label.pack(anchor="nw", padx=12, pady=(12,6))

        # FIX: Use lambda to defer the method call until it's defined
        self.btn_check = ctk.CTkButton(self.sidebar, text="Check GitHub Now", 
                                        command=lambda: self.manual_check(),
                                        fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                                        text_color="white", font=BUTTON_FONT, height=35)
        self.btn_check.pack(fill="x", padx=12, pady=(6,4))
        
        self.btn_open_folder = ctk.CTkButton(self.sidebar, text="Open Install Folder", 
                                              command=self.open_install_folder,
                                              fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                                              text_color="white", font=BUTTON_FONT, height=35)
        self.btn_open_folder.pack(fill="x", padx=12, pady=(0,6))
        
        # Access Status Display
        self.access_status_var = tk.StringVar(value="Status: Always Verified")
        self.access_status_label = ctk.CTkLabel(self.sidebar, textvariable=self.access_status_var, font=("Arial", 12, "bold"), text_color=SUCCESS_COLOR)
        self.access_status_label.pack(anchor="nw", padx=12, pady=(4, 8))

        # Macro list (Available Macros - Only show downloaded files)
        self.macro_scroll = ctk.CTkScrollableFrame(self.sidebar, label_text="Available Scripts", height=300)
        self.macro_scroll.pack(fill="both", expand=True, padx=12, pady=(6,6))
        self.macro_scroll.grid_columnconfigure(0, weight=1)
        
        self._build_ui_sidebar()

        # Bottom sidebar options
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(fill="x", side="bottom", padx=12, pady=10)
        
        # Launcher Version in gray text
        self.version_label = ctk.CTkLabel(bottom_frame, text="Launcher Version: v0.2.2 (Stability)", font=("Arial", 10, "bold"), text_color=GRAY_COLOR)
        self.version_label.pack(anchor="sw", padx=12, pady=(8,4))

        # Main frame (Column 1)
        self.main = ctk.CTkFrame(self, corner_radius=8)
        self.main.grid(row=0, column=1, sticky="nsew", padx=(8,12), pady=12)
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # Horizontal tab buttons - NOW 6 COLUMNS: Home, Settings, Social, Webhook, Updates, Credits
        self.tab_frame = ctk.CTkFrame(self.main)
        self.tab_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12,6))
        self.tab_frame.grid_columnconfigure((0,1,2,3,4,5), weight=1) 
        self.current_tab = "Home"
        
        self.tab_home_btn = ctk.CTkButton(self.tab_frame, text="Home", command=lambda:self._render_tab("Home"),
                                         fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                                         text_color="white", font=BUTTON_FONT, height=35)
        self.tab_home_btn.grid(row=0, column=0, sticky="ew", padx=4)
        
        self.tab_settings_btn = ctk.CTkButton(self.tab_frame, text="Settings", command=lambda:self._render_tab("Settings"),
                                              fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                                              text_color="white", font=BUTTON_FONT, height=35)
        self.tab_settings_btn.grid(row=0, column=1, sticky="ew", padx=4) 
        
        self.tab_social_btn = ctk.CTkButton(self.tab_frame, text="Social", command=lambda:self._render_tab("Social"),
                                              fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                                              text_color="white", font=BUTTON_FONT, height=35)
        self.tab_social_btn.grid(row=0, column=2, sticky="ew", padx=4)

        self.tab_webhook_btn = ctk.CTkButton(self.tab_frame, text="Webhook", command=lambda:self._render_tab("Webhook"),
                                              fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                                              text_color="white", font=BUTTON_FONT, height=35)
        self.tab_webhook_btn.grid(row=0, column=3, sticky="ew", padx=4)

        self.tab_updates_btn = ctk.CTkButton(self.tab_frame, text="Updates", command=lambda:self._render_tab("Updates"),
                                              fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                                              text_color="white", font=BUTTON_FONT, height=35)
        self.tab_updates_btn.grid(row=0, column=4, sticky="ew", padx=4) 

        self.tab_credits_btn = ctk.CTkButton(self.tab_frame, text="Credits", command=lambda:self._render_tab("Credits"),
                                              fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                                              text_color="white", font=BUTTON_FONT, height=35)
        self.tab_credits_btn.grid(row=0, column=5, sticky="ew", padx=4)

        # Content container
        self.content_container = ctk.CTkFrame(self.main)
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=12, pady=(6,6))
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        self._render_tab("Home") 

        # Console at bottom
        bottom = ctk.CTkFrame(self.main)
        bottom.grid(row=2, column=0, sticky="nsew", padx=12, pady=(6,12))
        bottom.grid_rowconfigure(0, weight=1)
        bottom.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(bottom, text="Console / Activity", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=6, pady=(6,4))
        self.console = ctk.CTkTextbox(bottom, height=160)
        self.console.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
        self.console.configure(state="disabled")
        
    def _update_access_status_display(self, is_verified):
        """Helper to update only the labels without rebuilding buttons (fixes blinking)."""
        time_remaining = self._get_time_remaining()
        
        if is_verified:
            status_text = f"Status: {time_remaining}"
            status_color = SUCCESS_COLOR
            # Update the macro scroll label text
            self.macro_scroll.configure(label_text=f"Available Scripts")
        else:
            status_text = "Status: Always Verified"
            status_color = SUCCESS_COLOR
            self.macro_scroll.configure(label_text="Available Scripts")

        self.access_status_var.set(status_text)
        self.access_status_label.configure(text_color=status_color)
    
    def _build_ui_sidebar(self):
        """
        Rebuilds the dynamic part of the sidebar (Available Macros) 
        """
        # Use a safe check that doesn't log to console during initial build
        is_verified = True  # Always verified now
        
        # 1. Update Access Status Display
        self._update_access_status_display(is_verified)
        
        # 2. Destroy existing macro buttons
        if hasattr(self, 'macro_scroll') and self.macro_scroll.winfo_children():
            for widget in self.macro_scroll.winfo_children():
                widget.destroy()
        
        # 3. Filter and create buttons
        i = 0
        for name, data in APP_MACROS.items():
            if self._is_file_downloaded(data["filename"]):
                
                btn_state = "normal"  # Always enabled now
                
                # Create a frame for each macro with name button and start button
                macro_frame = ctk.CTkFrame(self.macro_scroll, fg_color="transparent")
                macro_frame.grid(row=i, column=0, padx=8, pady=4, sticky="ew")
                macro_frame.grid_columnconfigure(0, weight=1)  # Name button takes most space
                macro_frame.grid_columnconfigure(1, weight=0)  # Start button fixed size
                
                # Macro name button (left side)
                name_btn = ctk.CTkButton(macro_frame, text=name,
                                        command=lambda n=name: self.load_macro_detail(n),
                                        fg_color=data["color"], hover_color=data["hover"],
                                        text_color="white", font=BUTTON_FONT, state=btn_state, height=35)
                name_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
                
                # START button (right side) - KEEP THIS IN SIDEBAR
                start_btn = ctk.CTkButton(macro_frame, text="START",
                                        command=lambda f=data["filename"]: self._start_macro_directly(f),
                                        fg_color=SUCCESS_COLOR, hover_color="#27ae60",
                                        text_color="white", font=("Arial", 10, "bold"), 
                                        width=60, height=35)
                start_btn.grid(row=0, column=1, sticky="e")
                
                i += 1
        
        # 4. Show a message if no macros are available
        if i == 0:
            ctk.CTkLabel(self.macro_scroll, text="No downloaded scripts available. Use the GitHub check button to update files.", wraplength=200, justify="left", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, padx=8, pady=6, sticky="ew")

    def _start_macro_directly(self, filename):
        """Start a macro directly from the sidebar START button"""
        # Find the macro name from the filename
        macro_name = None
        for name, data in APP_MACROS.items():
            if data["filename"] == filename:
                macro_name = name
                break
        
        if macro_name:
            log_console(self.console, f"Starting macro directly: {macro_name}")
            self.current_macro_name = macro_name
            
            # Send webhook notification
            self._send_macro_start_webhook(macro_name)
            
            # Run the macro directly
            macro_path = os.path.join(INSTALL_FOLDER, filename)
            if not os.path.exists(macro_path):
                log_console(self.console, f"ERROR: Script not found at {macro_path}.")
                messagebox.showerror("File Not Found", f"The script '{filename}' could not be found locally.")
                return

            self._is_macro_running = True
            self._start_macro_timer()
            log_console(self.console, f"Starting macro: {macro_name}...")
            
            threading.Thread(target=self._macro_execution_thread, args=(macro_path,), daemon=True).start()
        else:
            messagebox.showwarning("Macro Not Found", f"Could not find macro for file: {filename}")

    # --- TAB RENDERING ---
    def _render_tab(self, tab_name, macro_name=None):
        self.current_tab = tab_name
        for w in self.content_container.winfo_children():
            w.destroy()
            
        if tab_name=="Home":
            self._render_home_tab()
        elif tab_name=="Settings":
            self._render_settings_tab() 
        elif tab_name=="Social": 
            self._render_social_tab()
        elif tab_name=="Webhook":
            self._render_webhook_tab()
        elif tab_name=="Updates": 
            self._render_updates_tab()
        elif tab_name=="Credits":
            self._render_credits_tab() 
        elif tab_name=="MacroDetail" and macro_name:
            self._render_macro_detail_tab(macro_name)
            
    # --- HOME TAB IMPLEMENTATION ---
    def _render_home_tab(self):
        """Renders the main welcome/home tab."""
        content_frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")  # Changed to scrollable
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content_frame, text="Welcome to 2OP Macro Client", 
                    font=("Arial", 24, "bold"), text_color="#1f6feb").pack(anchor="center", pady=20)
        
        info_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=10)  # Reduced padding
        
        info_text = """• Select a script from the sidebar to view details and start
• Use the "Check GitHub Now" button to download the latest files
• All macros are available without verification
• Enable Discord webhook in the Webhook tab for live updates"""
        
        ctk.CTkLabel(info_frame, text=info_text, font=("Arial", 14), 
                    justify="left", wraplength=750).pack(padx=15, pady=15)  # Added wraplength
        
    # --- SETTINGS TAB IMPLEMENTATION ---
    def _on_theme_change(self, new_theme):
        """Handles changing the CustomTkinter theme."""
        ctk.set_appearance_mode(new_theme)
        log_console(self.console, f"Appearance theme set to '{new_theme}'.")
        self._save_current_settings()
        
    def _on_resolution_change(self, new_resolution):
        """Handles changing the window resolution."""
        try:
            self.geometry(new_resolution)
            self._save_current_settings()
            log_console(self.console, f"Resolution set to '{new_resolution}'.")
        except Exception as e:
            log_console(self.console, f"Error setting resolution: {e}")
        
    def _on_auto_update_change(self):
        """Handles auto-update checkbox changes and saves settings."""
        self.auto_update_on_start = self.update_settings_var.get()
        self._save_current_settings()
        
    def _render_settings_tab(self):
        """Renders the Settings tab using a scrollable frame."""
        scroll_frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        scroll_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(scroll_frame, text="Client Settings", font=("Arial", 24, "bold"), text_color="#1f6feb").pack(anchor="nw", pady=(10, 20))
        
        # --- Update Settings ---
        update_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        update_frame.pack(fill="x", pady=(10, 20), padx=5)
        ctk.CTkLabel(update_frame, text="Update Management", font=("Arial", 16, "bold")).pack(anchor="nw", padx=15, pady=(15, 5))
        
        # Auto-update on startup
        ctk.CTkLabel(update_frame, text="Auto-update on startup:", font=("Arial", 14)).pack(anchor="nw", padx=15, pady=(5, 0))
        self.update_settings_var = tk.BooleanVar(value=self.auto_update_on_start)
        self.update_settings_check = ctk.CTkCheckBox(update_frame, text="Enable automatic GitHub check when client launches.", 
                                                    variable=self.update_settings_var, command=self._on_auto_update_change)
        self.update_settings_check.pack(anchor="nw", padx=15, pady=(0, 15))

        # --- Appearance Settings ---
        appearance_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        appearance_frame.pack(fill="x", pady=(10, 20), padx=5)
        ctk.CTkLabel(appearance_frame, text="Appearance and Theme", font=("Arial", 16, "bold")).pack(anchor="nw", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(appearance_frame, text="Select Theme:", font=("Arial", 14)).pack(anchor="nw", padx=15, pady=(5, 0))
        theme_options = ctk.CTkOptionMenu(appearance_frame, values=["Dark", "Light", "System"], 
                                         command=self._on_theme_change, width=150)
        theme_options.set(ctk.get_appearance_mode())
        theme_options.pack(anchor="nw", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(appearance_frame, text="Select Resolution:", font=("Arial", 14)).pack(anchor="nw", padx=15, pady=(10, 0))
        resolution_options = ctk.CTkOptionMenu(appearance_frame, 
                                             values=["800x600", "920x640", "1024x768", "1280x720"], 
                                             command=self._on_resolution_change, width=150)
        current_res = f"{self.winfo_width()}x{self.winfo_height()}"
        resolution_options.set(current_res)
        resolution_options.pack(anchor="nw", padx=15, pady=(0, 15))

        # --- Debug/Maintenance ---
        maintenance_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        maintenance_frame.pack(fill="x", pady=(10, 20), padx=5)
        ctk.CTkLabel(maintenance_frame, text="Maintenance and Debug", font=("Arial", 16, "bold")).pack(anchor="nw", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(maintenance_frame, text="Client Version: v0.2.2 (Stability)", font=("Arial", 12)).pack(anchor="nw", padx=15, pady=(5, 0))
        
        # Link to Discord (Reference to Social Tab)
        ctk.CTkLabel(maintenance_frame, text="Discord Server Link:", font=("Arial", 14)).pack(anchor="nw", padx=15, pady=(10, 0))
        discord_url = f"https://discord.gg/{DISCORD_SERVER_ID}"
        discord_link = ctk.CTkLabel(maintenance_frame, text="Click here to join the official 2OP Discord server.", 
                                   text_color="#5865F2", cursor="hand2", font=("Arial", 14, "underline"), anchor="w")
        discord_link.bind("<Button-1>", lambda e: self._open_url(discord_url))
        discord_link.pack(anchor="nw", padx=15, pady=(0, 15))

    # --- SOCIAL TAB IMPLEMENTATION ---
    def _open_url(self, url):
        """Opens the given URL in a new browser tab."""
        try:
            webbrowser.open_new_tab(url)
            log_console(self.console, f"Opening URL: {url}")
        except Exception as e:
            log_console(self.console, f"Failed to open URL {url}: {e}")

    def _render_social_tab(self):
        """Renders the Social tab with all links and the prominent Discord verification button."""
        scroll_frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")  # Changed to scrollable
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(scroll_frame, text="2OP Social Hub", font=("Arial", 24, "bold"), text_color="#1f6feb").pack(anchor="nw", pady=(10, 10))
        
        # --- Discord Rank/Verification Section ---
        rank_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        rank_frame.pack(fill="x", pady=(10, 20)) 
        
        ctk.CTkLabel(rank_frame, text="Discord Community", 
                    font=("Arial", 16, "bold")).pack(anchor="nw", padx=15, pady=(15, 5))
        
        info_text = """Join our Discord community for updates, support, and to connect with other users."""
        
        ctk.CTkLabel(rank_frame, text=info_text, wraplength=750, justify="left").pack(anchor="nw", padx=15, pady=(0, 15))

        discord_button_frame = ctk.CTkFrame(rank_frame, fg_color="transparent")
        discord_button_frame.pack(fill="x", padx=15, pady=(0, 20))
        
        # Discord verification section
        ctk.CTkButton(discord_button_frame, 
                      text="Join Discord Server", 
                      command=lambda: self._open_url(f"https://discord.gg/{DISCORD_SERVER_ID}"),
                      fg_color=DISCORD_COLOR, 
                      hover_color=DISCORD_HOVER,
                      text_color="white", 
                      font=("Arial", 14, "bold"),
                      height=40, width=200).pack(side="left", padx=5)
        
        current_status_text = f"Current Access: Always Verified"
        current_status_color = SUCCESS_COLOR
        ctk.CTkLabel(discord_button_frame, text=current_status_text, font=("Arial", 12, "bold"), text_color=current_status_color).pack(side="left", padx=15)

        # --- Social Links Section ---
        links_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        links_frame.pack(fill="x", pady=(10, 20))
        ctk.CTkLabel(links_frame, text="Official Links (Support & Content)", font=("Arial", 16, "bold")).pack(anchor="nw", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(links_frame, text="Ko-fi (Support): ", font=("Arial", 14, "bold")).pack(anchor="nw", padx=15, pady=(5, 0))
        kofi_url = "https://ko-fi.com/Youngblock2k/tip"
        kofi_link = ctk.CTkLabel(links_frame, text=kofi_url, text_color="#e74c3c", cursor="hand2", font=("Arial", 14), anchor="w")
        kofi_link.bind("<Button-1>", lambda e: self._open_url(kofi_url))
        kofi_link.pack(anchor="nw", padx=15, pady=(0, 5))

        ctk.CTkLabel(links_frame, text="YouTube Channel: ", font=("Arial", 14, "bold")).pack(anchor="nw", padx=15, pady=(5, 0))
        youtube_url = "https://www.youtube.com/@Youngblock2k" 
        youtube_link = ctk.CTkLabel(links_frame, text="Youngblock2k", text_color="#f39c12", cursor="hand2", font=("Arial", 14), anchor="w")
        youtube_link.bind("<Button-1>", lambda e: self._open_url(youtube_url))
        youtube_link.pack(anchor="nw", padx=15, pady=(0, 15))

    # --- WEBHOOK TAB IMPLEMENTATION ---
    def _render_webhook_tab(self):
        """Renders the Webhook tab for Discord webhook configuration."""
        scroll_frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(scroll_frame, text="Discord Webhook Settings", 
                    font=("Arial", 24, "bold"), text_color="#1f6feb").pack(anchor="nw", pady=(10, 20))
        
        # Info frame
        info_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        info_frame.pack(fill="x", pady=(10, 20))
        info_text = """**Discord Webhook Features:**
• Live status updates every 30 seconds
• Macro start/stop notifications  
• Recent activity logs
• Runtime tracking
• Embed messages with colors

**How to set up:**
1. Go to your Discord server settings
2. Navigate to Integrations → Webhooks
3. Create a new webhook
4. Copy the webhook URL and paste it below
5. Enable webhook monitoring"""
        
        ctk.CTkLabel(info_frame, text=info_text, font=("Arial", 14), justify="left", wraplength=800).pack(padx=15, pady=15)
        
        # Webhook URL input
        webhook_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        webhook_frame.pack(fill="x", pady=(10, 20))
        ctk.CTkLabel(webhook_frame, text="Discord Webhook URL:", font=("Arial", 16, "bold")).pack(anchor="nw", padx=15, pady=(15, 5))
        
        self.webhook_url_entry = ctk.CTkEntry(webhook_frame, placeholder_text="https://discord.com/api/webhooks/...", width=400, height=35)
        self.webhook_url_entry.insert(0, self.webhook_url)
        self.webhook_url_entry.pack(anchor="nw", padx=15, pady=(0, 10))
        
        # Webhook enabled checkbox
        self.webhook_enabled_var = tk.BooleanVar(value=self.webhook_enabled)
        self.webhook_enabled_check = ctk.CTkCheckBox(webhook_frame, text="Enable Discord webhook monitoring", 
                                                   variable=self.webhook_enabled_var, font=("Arial", 14))
        self.webhook_enabled_check.pack(anchor="nw", padx=15, pady=(0, 15))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 20))
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Test webhook button
        test_btn = ctk.CTkButton(buttons_frame, 
                               text="Test Webhook", 
                               command=self._test_webhook,
                               fg_color="#3498db", 
                               hover_color="#2980b9",
                               text_color="white", 
                               font=("Arial", 14, "bold"),
                               height=40)
        test_btn.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Save settings button
        save_btn = ctk.CTkButton(buttons_frame, 
                               text="Save Settings", 
                               command=self._save_webhook_settings,
                               fg_color=SUCCESS_COLOR, 
                               hover_color="#27ae60",
                               text_color="white", 
                               font=("Arial", 14, "bold"),
                               height=40)
        save_btn.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # View logs button
        view_logs_btn = ctk.CTkButton(buttons_frame, 
                                    text="View Logs", 
                                    command=self._open_webhook_file,
                                    fg_color=BUTTON_FG_COLOR, 
                                    hover_color=BUTTON_HOVER_COLOR,
                                    text_color="white", 
                                    font=("Arial", 14, "bold"),
                                    height=40)
        view_logs_btn.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        
        # Status indicator
        status_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        status_frame.pack(fill="x", pady=(10, 20))
        
        status_text = "🔴 Webhook Disabled"
        status_color = WARNING_COLOR
        if self.webhook_enabled and self.webhook_url:
            status_text = "🟢 Webhook Active - Sending live updates every 30 seconds"
            status_color = SUCCESS_COLOR
        elif self.webhook_url and not self.webhook_enabled:
            status_text = "🟡 Webhook Configured - Enable monitoring to start"
            status_color = "#f39c12"
            
        ctk.CTkLabel(status_frame, text=status_text, font=("Arial", 14, "bold"), text_color=status_color).pack(padx=15, pady=15)

    def _open_webhook_file(self):
        """Opens the webhook.txt file in the default text editor."""
        try:
            if os.path.exists(WEBHOOK_FILE):
                if sys.platform == "win32":
                    os.startfile(WEBHOOK_FILE)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", WEBHOOK_FILE])
                else:
                    subprocess.Popen(["xdg-open", WEBHOOK_FILE])
                log_console(self.console, "Opened webhook.txt file")
            else:
                messagebox.showinfo("File Not Found", "webhook.txt file does not exist yet.")
        except Exception as e:
            log_console(self.console, f"Error opening webhook file: {e}")
            messagebox.showerror("Error", f"Could not open webhook.txt: {e}")

    # --- UPDATES TAB IMPLEMENTATION ---
    def _render_updates_tab(self):
        """Renders the Updates tab with unified scroll and cleaner layout."""
        scroll_frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Header
        ctk.CTkLabel(scroll_frame, text="🚀 Repository Manager", 
                    font=("Arial", 28, "bold"), text_color="#1f6feb").pack(anchor="nw", pady=(10, 5))
        ctk.CTkLabel(scroll_frame, text="Manage and update your macro files from GitHub", 
                    font=("Arial", 14), text_color="gray").pack(anchor="nw", pady=(0, 20))
        
        # Control Buttons Frame
        control_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        control_frame.pack(fill="x", pady=(0, 20))
        control_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.update_all_btn = ctk.CTkButton(control_frame, 
                                            text="🔄 UPDATE ALL FILES",
                                            command=self._update_all_files,
                                            fg_color="#27ae60",
                                            hover_color="#219a52",
                                            text_color="white",
                                            font=("Arial", 14, "bold"),
                                            height=40)
        self.update_all_btn.grid(row=0, column=0, padx=10, pady=15, sticky="ew")

        self.refresh_list_btn = ctk.CTkButton(control_frame, 
                                            text="📋 REFRESH LIST",
                                            command=self._refresh_repo_files,
                                            fg_color="#3498db",
                                            hover_color="#2980b9",
                                            text_color="white",
                                            font=("Arial", 14, "bold"),
                                            height=40)
        self.refresh_list_btn.grid(row=0, column=1, padx=10, pady=15, sticky="ew")

        self.github_btn = ctk.CTkButton(control_frame, 
                                        text="🌐 OPEN GITHUB",
                                        command=lambda: self._open_url(f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}"),
                                        fg_color="#9b59b6",
                                        hover_color="#8e44ad",
                                        text_color="white",
                                        font=("Arial", 14, "bold"),
                                        height=40)
        self.github_btn.grid(row=0, column=2, padx=10, pady=15, sticky="ew")

        # Files list directly inside scrollable frame (no nested scrollbar)
        self.files_container = ctk.CTkFrame(scroll_frame, corner_radius=10)
        self.files_container.pack(fill="both", expand=True, pady=(0, 20))

        ctk.CTkLabel(self.files_container, text="📁 Repository Files", 
                    font=("Arial", 18, "bold")).pack(anchor="nw", padx=15, pady=(15, 10))
        
        # Frame to hold file entries
        self.files_list_frame = ctk.CTkFrame(self.files_container, fg_color="transparent")
        self.files_list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Status Frame
        self.status_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        self.status_frame.pack(fill="x", pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(self.status_frame, 
                                        text="🔄 Loading repository files...", 
                                        font=("Arial", 12),
                                        justify="left",
                                        wraplength=800)
        self.status_label.pack(padx=15, pady=15, anchor="w")
        
        threading.Thread(target=self._load_repo_files_for_updates, daemon=True).start()


    def _load_repo_files_for_updates(self):
        """Loads repository files for the updates tab."""
        try:
            self.after(0, lambda: self.status_label.configure(text="🔄 Connecting to GitHub..."))
            
            # Fetch repository contents
            repo_data = safe_request_json(f"{GITHUB_API_CONTENTS}?ref=main")
            if not repo_data:
                self.after(0, lambda: self.status_label.configure(
                    text="❌ Failed to connect to GitHub. Please check your internet connection."
                ))
                return
            
            # Filter for Python files only
            self.repo_files = [
                f for f in repo_data 
                if f.get('type') == 'file' and f.get('name', '').endswith('.py')
            ]
            
            if not self.repo_files:
                self.after(0, lambda: self.status_label.configure(
                    text="📭 No Python files found in the repository."
                ))
                return
            
            # Update the UI with files list
            self.after(0, self._update_files_list_ui)
            
            self.after(0, lambda: self.status_label.configure(
                text=f"✅ Loaded {len(self.repo_files)} Python files from repository."
            ))
            
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(
                text=f"❌ Error loading repository: {str(e)}"
            ))

    def _update_files_list_ui(self):
        """Updates the repository file list inside the Updates tab."""
        for widget in self.files_list_frame.winfo_children():
            widget.destroy()

        if not self.repo_files:
            ctk.CTkLabel(self.files_list_frame, 
                        text="No files found in repository.",
                        font=("Arial", 14),
                        text_color="gray").pack(pady=20)
            return

        self._refresh_app_macros_from_local_files()

        for remote_file in self.repo_files:
            filename = remote_file['name']
            remote_sha = remote_file['sha']
            download_url = remote_file['download_url']
            size_kb = f"{remote_file.get('size', 0) / 1024:.1f} KB"

            local_sha = self.local_files.get(filename)
            file_status = self._get_file_status(filename, local_sha, remote_sha)

            file_frame = ctk.CTkFrame(self.files_list_frame, corner_radius=8)
            file_frame.pack(fill="x", padx=5, pady=5)
            file_frame.grid_columnconfigure(0, weight=1)

            # File info text
            file_icon = "🐍" if filename.endswith('.py') else "📄"
            ctk.CTkLabel(file_frame, text=f"{file_icon} {filename}", 
                        font=("Arial", 14, "bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))

            status_color = {
                "up_to_date": "#27ae60",
                "outdated": "#e67e22", 
                "not_downloaded": "#e74c3c",
                "unknown": "#95a5a6"
            }.get(file_status, "#95a5a6")

            status_text = {
                "up_to_date": "✅ UP TO DATE",
                "outdated": "🔄 UPDATE AVAILABLE", 
                "not_downloaded": "📥 DOWNLOAD",
                "unknown": "❓ UNKNOWN STATUS"
            }.get(file_status, "❓ UNKNOWN")

            ctk.CTkLabel(file_frame, text=f"{status_text} • {size_kb}",
                        text_color=status_color,
                        font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))

            # Action button
            if file_status == "up_to_date":
                btn_text, btn_color, hover_color, state = "DOWNLOADED", "#27ae60", "#219a52", "disabled"
            elif file_status == "outdated":
                btn_text, btn_color, hover_color, state = "UPDATE", "#e67e22", "#d35400", "normal"
            else:
                btn_text, btn_color, hover_color, state = "DOWNLOAD", "#3498db", "#2980b9", "normal"

            ctk.CTkButton(file_frame, text=btn_text,
                        command=lambda f=filename, u=download_url: self._update_single_file(f, u),
                        fg_color=btn_color,
                        hover_color=hover_color,
                        text_color="white",
                        font=("Arial", 12, "bold"),
                        width=120,
                        height=32,
                        state=state).grid(row=0, column=1, rowspan=2, padx=10, pady=8, sticky="e")


    def _get_file_status(self, filename, local_sha, remote_sha):
        """Determines the status of a file."""
        if local_sha is None:
            return "not_downloaded"
        elif local_sha == remote_sha:
            return "up_to_date"
        elif local_sha != remote_sha:
            return "outdated"
        else:
            return "unknown"

    def _update_all_files(self):
        """Updates all files that need updating.""" 
        if not self.repo_files:
            messagebox.showwarning("No Files", "No repository files loaded. Please refresh the list first.")
            return
        
        # Count files that need updating
        files_to_update = []
        for remote_file in self.repo_files:
            filename = remote_file['name']
            remote_sha = remote_file['sha']
            local_sha = self.local_files.get(filename)
            
            if local_sha != remote_sha:  # Includes both outdated and not downloaded
                files_to_update.append(remote_file)
        
        if not files_to_update:
            messagebox.showinfo("Up to Date", "All files are already up to date!")
            return
        
        # Confirm update
        result = messagebox.askyesno(
            "Update All Files", 
            f"Update {len(files_to_update)} file(s)?\n\nThis will download/update:\n" + 
            "\n".join([f"• {f['name']}" for f in files_to_update])
        )
        
        if not result:
            return
        
        # Start update process
        threading.Thread(target=self._update_all_files_thread, args=(files_to_update,), daemon=True).start()

    def _update_all_files_thread(self, files_to_update):
        """Thread function to update all files."""
        self.after(0, lambda: self.status_label.configure(
            text=f"🔄 Updating {len(files_to_update)} file(s)..."
        ))
        
        success_count = 0
        failed_files = []
        
        for remote_file in files_to_update:
            filename = remote_file['name']
            download_url = remote_file['download_url']
            filepath = os.path.join(INSTALL_FOLDER, filename)
            
            self.after(0, lambda f=filename: self.status_label.configure(
                text=f"📥 Downloading {f}..."
            ))
            
            if download_file(download_url, filepath):
                success_count += 1
                log_console(self.console, f"✅ Updated: {filename}")
            else:
                failed_files.append(filename)
                log_console(self.console, f"❌ Failed to update: {filename}")
        
        # Update UI and show results
        self.after(0, self._refresh_app_macros_from_local_files)
        self.after(0, self._update_files_list_ui)
        self.after(0, self._trigger_sidebar_rebuild)
        
        if failed_files:
            self.after(0, lambda: self.status_label.configure(
                text=f"⚠️ Updated {success_count}/{len(files_to_update)} files. Failed: {', '.join(failed_files)}"
            ))
            messagebox.showwarning(
                "Update Complete with Errors",
                f"Updated {success_count} file(s) successfully.\n\nFailed to update:\n" + "\n".join(failed_files)
            )
        else:
            self.after(0, lambda: self.status_label.configure(
                text=f"✅ Successfully updated {success_count} file(s)!"
            ))
            messagebox.showinfo("Update Complete", f"Successfully updated {success_count} file(s)!")

    def _update_single_file(self, filename, download_url):
        """Updates a single file."""
        filepath = os.path.join(INSTALL_FOLDER, filename)
        
        self.after(0, lambda: self.status_label.configure(
            text=f"📥 Downloading {filename}..."
        ))
        
        def update_thread():
            if download_file(download_url, filepath):
                log_console(self.console, f"✅ Updated: {filename}")
                self.after(0, self._refresh_app_macros_from_local_files)
                self.after(0, self._update_files_list_ui)
                self.after(0, self._trigger_sidebar_rebuild)
                self.after(0, lambda: self.status_label.configure(
                    text=f"✅ Successfully updated {filename}!"
                ))
                messagebox.showinfo("Update Complete", f"Successfully updated {filename}!")
            else:
                log_console(self.console, f"❌ Failed to update: {filename}")
                self.after(0, lambda: self.status_label.configure(
                    text=f"❌ Failed to update {filename}"
                ))
                messagebox.showerror("Update Failed", f"Failed to update {filename}. Please check your connection.")
        
        threading.Thread(target=update_thread, daemon=True).start()

    def _refresh_repo_files(self):
        """Refreshes the repository files list."""
        self.after(0, lambda: self.status_label.configure(
            text="🔄 Refreshing repository files..."
        ))
        threading.Thread(target=self._load_repo_files_for_updates, daemon=True).start()

    # --- CREDITS TAB IMPLEMENTATION ---
    def _render_credits_tab(self):
        """Renders the modern Credits tab with names only."""
        scroll_frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Title
        ctk.CTkLabel(
            scroll_frame,
            text="Credits & Acknowledgements",
            font=("Arial", 28, "bold"),
            text_color="#1f6feb"
        ).pack(anchor="nw", pady=(10, 20))
        
        # --- Main Developer ---
        main_frame = ctk.CTkFrame(scroll_frame, corner_radius=12)
        main_frame.pack(fill="x", pady=(10, 15))
        ctk.CTkLabel(main_frame, text="Primary Developer", font=("Arial", 18, "bold")).pack(anchor="nw", padx=15, pady=(10, 0))
        ctk.CTkLabel(main_frame, text="Youngblock2k", font=("Arial", 16)).pack(anchor="nw", padx=15, pady=(0, 10))
        
        # --- Contributors ---
        contrib_frame = ctk.CTkFrame(scroll_frame, corner_radius=12)
        contrib_frame.pack(fill="x", pady=(10, 15))
        ctk.CTkLabel(contrib_frame, text="Contributors", font=("Arial", 18, "bold")).pack(anchor="nw", padx=15, pady=(10, 0))
        contributors = ["Ascyt,Goofy Knight, Bgsigood"]
        for name in contributors:
            ctk.CTkLabel(contrib_frame, text=f"- {name}", font=("Arial", 16)).pack(anchor="nw", padx=20, pady=(2, 2))
        
        # --- Supporters ---
        support_frame = ctk.CTkFrame(scroll_frame, corner_radius=12)
        support_frame.pack(fill="x", pady=(10, 15))
        ctk.CTkLabel(support_frame, text="Special Thanks", font=("Arial", 18, "bold")).pack(anchor="nw", padx=15, pady=(10, 0))
        supporters = ["2OP Community", "Early Testers", "Discord Team"]
        for name in supporters:
            ctk.CTkLabel(support_frame, text=f"- {name}", font=("Arial", 16)).pack(anchor="nw", padx=20, pady=(2, 2))
        
        # --- Footer ---
        ctk.CTkLabel(
            scroll_frame,
            text="Thank you to everyone who contributed to 2OP's growth and success!",
            font=("Arial", 14, "italic"),
            text_color="#a0a0a0",
            wraplength=750,
            justify="center"
        ).pack(anchor="center", pady=20)

    # --- MACRO DETAIL TAB IMPLEMENTATION (NEW) ---
    def load_macro_detail(self, macro_name):
        """Loads the MacroDetail tab for the selected macro."""
        self._render_tab("MacroDetail", macro_name)

    def _render_macro_detail_tab(self, macro_name):
        """Renders the macro detail, run/stop button, and runtime display."""
        self.current_macro_name = macro_name
        data = APP_MACROS.get(macro_name, {})
        filename = data.get("filename", "N/A")
        description = data.get("description", "No description available.")
        version = data.get("version", "Unknown version")

        # Header Frame
        header_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(header_frame, text=macro_name, font=("Arial", 32, "bold"), text_color="#1f6feb").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header_frame, text=f"File: {filename} | Version: {version}", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=(0, 10))

        # Description
        ctk.CTkLabel(self.content_container, text="Description:", font=("Arial", 16, "bold")).pack(anchor="nw", padx=30, pady=(10, 0))
        ctk.CTkLabel(self.content_container, text=description, wraplength=850, justify="left", font=("Arial", 14)).pack(anchor="nw", padx=30, pady=(0, 20))

        # Control Frame
        control_frame = ctk.CTkFrame(self.content_container, corner_radius=10, fg_color=GRAY_COLOR)
        control_frame.pack(fill="x", padx=30, pady=20)
        control_frame.grid_columnconfigure((0, 1), weight=1)

        # Run/Stop Button
        self.run_stop_button = ctk.CTkButton(control_frame, 
                                            text="Run Macro", 
                                            command=self.toggle_macro_execution,
                                            fg_color=SUCCESS_COLOR,
                                            hover_color="#27ae60",
                                            text_color="white", 
                                            font=("Arial", 18, "bold"),
                                            height=50)
        self.run_stop_button.grid(row=0, column=0, padx=15, pady=15, sticky="ew")

        # Runtime Display
        runtime_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        runtime_frame.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        ctk.CTkLabel(runtime_frame, text="Current Runtime:", font=("Arial", 14, "bold")).pack(anchor="nw")
        self.macro_runtime_label = ctk.CTkLabel(runtime_frame, textvariable=self.macro_runtime_var, font=("Arial", 28, "bold"), text_color="#f1c40f")
        self.macro_runtime_label.pack(anchor="nw")

        # Update button state based on current running status
        self._update_run_stop_button_ui()

    # --- MACRO EXECUTION LOGIC (NEW) ---
    def _update_run_stop_button_ui(self):
        """Updates the Run/Stop button text and color based on the macro state."""
        if not hasattr(self, 'run_stop_button'):
            return

        if self._is_macro_running:
            self.run_stop_button.configure(text="STOP Macro", fg_color=WARNING_COLOR, hover_color="#c0392b")
        else:
            self.run_stop_button.configure(text="Run Macro", fg_color=SUCCESS_COLOR, hover_color="#27ae60")

    def toggle_macro_execution(self):
        """Main handler for the Run/Stop button."""
        if self._is_macro_running:
            self._stop_macro()
        else:
            # ALL MACROS ARE ALLOWED WITHOUT VERIFICATION
            self._run_macro()

    def _run_macro(self):
        """Starts the selected macro in a separate thread/subprocess."""
        if not self.current_macro_name:
            log_console(self.console, "ERROR: No macro selected.")
            return

        macro_filename = APP_MACROS.get(self.current_macro_name, {}).get("filename")
        if not macro_filename:
            log_console(self.console, f"ERROR: Could not find filename for macro: {self.current_macro_name}")
            return
            
        macro_path = os.path.join(INSTALL_FOLDER, macro_filename)
        if not os.path.exists(macro_path):
            log_console(self.console, f"ERROR: Script not found at {macro_path}. Please update from GitHub.")
            messagebox.showerror("File Not Found", f"The script '{macro_filename}' could not be found locally.")
            return

        self._is_macro_running = True
        self._update_run_stop_button_ui()
        self._start_macro_timer()
        log_console(self.console, f"Starting macro: {self.current_macro_name}...")
        
        # Send webhook notification
        self._send_macro_start_webhook(self.current_macro_name)
        
        threading.Thread(target=self._macro_execution_thread, args=(macro_path,), daemon=True).start()


            
    def _macro_execution_thread(self, script_path):
        """Launch macro in a visible command prompt window - Simple Method"""
        try:
            macro_name = os.path.basename(script_path)
            log_console(self.console, f"🚀 Launching macro: {macro_name}")

            # Get Python interpreter
            python_exe = self._get_real_python()
            if not python_exe:
                log_console(self.console, "❌ No system Python found.")
                messagebox.showerror("Python Not Found", "No system Python installation found.")
                return

            log_console(self.console, f"📂 Using interpreter: {python_exe}")
            
            # Simple method using os.system - most reliable for opening windows
            cmd = (
                f'start "2OP Macro - {macro_name}" '
                f'cmd /k "cd /d "{INSTALL_FOLDER}" && "{python_exe}" "{script_path}" && pause"'
            )
            
            log_console(self.console, f"🪟 Opening command prompt window...")
            
            # Use os.system which is very reliable for opening new windows
            os.system(cmd)
            
            log_console(self.console, f"✅ Command prompt window opened for: {macro_name}")

        except Exception as e:
            log_console(self.console, f"❌ Failed to start macro: {e}")
            messagebox.showerror("Error", f"Failed to start macro:\n{e}")
            self._is_macro_running = False
            self.after(0, self._update_run_stop_button_ui)
            self.after(0, self._stop_macro_timer)

    def _get_real_python(self):
        """Finds the correct Python interpreter (not the EXE itself)."""
        # Common Python install locations
        possible_pythons = [
            # User installations
            rf"C:\Users\{os.getlogin()}\AppData\Local\Programs\Python\Python312\python.exe",
            rf"C:\Users\{os.getlogin()}\AppData\Local\Programs\Python\Python311\python.exe",
            rf"C:\Users\{os.getlogin()}\AppData\Local\Programs\Python\Python310\python.exe",
            rf"C:\Users\{os.getlogin()}\AppData\Local\Programs\Python\Python39\python.exe",
            rf"C:\Users\{os.getlogin()}\AppData\Local\Programs\Python\Python38\python.exe",
            # System-wide installations
            r"C:\Program Files\Python312\python.exe",
            r"C:\Program Files\Python311\python.exe",
            r"C:\Program Files\Python310\python.exe",
            r"C:\Program Files\Python39\python.exe",
            r"C:\Program Files\Python38\python.exe",
            r"C:\Program Files (x86)\Python312\python.exe",
            r"C:\Program Files (x86)\Python311\python.exe",
            r"C:\Program Files (x86)\Python310\python.exe",
            r"C:\Program Files (x86)\Python39\python.exe",
            r"C:\Program Files (x86)\Python38\python.exe"
        ]
        
        # Check all possible Python installations
        for path in possible_pythons:
            if os.path.exists(path):
                # Double-check it's not our own EXE
                if hasattr(sys, 'frozen') and os.path.exists(sys.executable):
                    try:
                        if not os.path.samefile(path, sys.executable):
                            return path
                    except OSError:
                        # If samefile fails, compare paths
                        if os.path.normpath(path) != os.path.normpath(sys.executable):
                            return path
                else:
                    return path

        # Try PATH-based python or py launcher
        for cmd in ["python", "py"]:
            found = shutil.which(cmd)
            if found:
                # Double-check it's not our own EXE
                if hasattr(sys, 'frozen') and os.path.exists(sys.executable):
                    try:
                        if not os.path.samefile(found, sys.executable):
                            return found
                    except OSError:
                        if os.path.normpath(found) != os.path.normpath(sys.executable):
                            return found
                else:
                    return found

        return None

    def emergency_stop(self):
        """Force stop everything"""
        import subprocess
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], capture_output=True)
        subprocess.run(['taskkill', '/f', '/im', 'cmd.exe'], capture_output=True)
        self._is_macro_running = False
        self.after(0, self._update_run_stop_button_ui)
        self.after(0, self._stop_macro_timer)
        log_console(self.console, "🛑 EMERGENCY STOP: All processes killed")

    def _stop_macro(self):
        """Attempts to cleanly stop the running macro subprocess."""
        with self.proc_lock:
            if self.proc and self.proc.poll() is None:
                log_console(self.console, f"Stopping macro: {self.current_macro_name}...")
                try:
                    # Terminate the process (sends SIGTERM on POSIX, TerminateProcess on Windows)
                    self.proc.terminate() 
                    
                    # Give it a moment to terminate
                    try:
                        self.proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        log_console(self.console, "Macro process did not terminate gracefully, forcing kill.")
                        self.proc.kill()
                        
                    log_console(self.console, f"Macro '{self.current_macro_name}' stopped successfully.")
                except Exception as e:
                    log_console(self.console, f"Error stopping process: {e}")
                finally:
                    self.proc = None
                    
        self._is_macro_running = False
        self.after(0, self._update_run_stop_button_ui)
        
        # Calculate runtime and send webhook notification
        if self.macro_start_time:
            elapsed_seconds = int(time.time() - self.macro_start_time)
            hours = elapsed_seconds // 3600
            minutes = (elapsed_seconds % 3600) // 60
            seconds = elapsed_seconds % 60
            runtime = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
            self._send_macro_stop_webhook(self.current_macro_name, runtime)
        
        self.after(0, self._stop_macro_timer)



    def test_console_visibility(self):
        """Test if console windows are actually visible"""
        log_console(self.console, "🔍 Testing console visibility...")
        
        python_exe = self._get_real_python()
        if python_exe:
            try:
                # Test with a simple Python command that should show a console
                test_cmd = f'cmd /k "echo Console Visibility Test && {python_exe} -c \"print(\\\"Python is working!\\\"); input(\\\"Press Enter to close...\\\")\""'
                
                subprocess.Popen(test_cmd, shell=True)
                log_console(self.console, "✅ Console test launched - you should see a window")
                
            except Exception as e:
                log_console(self.console, f"❌ Console test failed: {e}")

    # --- GITHUB UPDATE LOGIC (NEW) ---
    def manual_check(self):
        """Public entry point for the 'Check GitHub Now' button."""
        log_console(self.console, "Manual check requested. Starting update thread...")
        threading.Thread(target=self._manual_update_thread, daemon=True).start()

    def _manual_update_thread(self):
        """Fetches file list, compares SHAs, deletes old files, and downloads new ones."""
        log_console(self.console, "Fetching remote file list from GitHub...")

        # 1. Fetch remote file list
        repo_data = safe_request_json(f"{GITHUB_API_CONTENTS}?ref=main")
        if not repo_data:
            log_console(self.console, "❌ ERROR: Failed to connect to GitHub API or repository is private/non-existent.")
            return

        # Include all files (py, txt, etc.)
        self.repo_files = [f for f in repo_data if f.get('type') == 'file']

        if not self.repo_files:
            log_console(self.console, "⚠️ WARNING: No files found in the remote repository.")
            return

        # Log file list
        file_names = [f['name'] for f in self.repo_files]
        log_console(self.console, f"📦 Found {len(self.repo_files)} files in repository: {', '.join(file_names)}")

        updates_found = 0
        failed_files = []

        # 2. Refresh local SHAs
        self.after(0, self._refresh_app_macros_from_local_files)

        # 3. Compare and Download
        for remote_file in self.repo_files:
            filename = remote_file['name']
            remote_sha = remote_file['sha']
            local_sha = self.local_files.get(filename)
            download_url = remote_file['download_url']
            filepath = os.path.join(INSTALL_FOLDER, filename)

            # If new file or changed file → delete old + re-download
            if local_sha is None:
                log_console(self.console, f"🆕 Found NEW file: {filename}. Downloading...")
            elif local_sha != remote_sha:
                log_console(self.console, f"🔄 Found UPDATED file: {filename}. Replacing old version...")
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        log_console(self.console, f"🗑️ Deleted old file: {filename}")
                except Exception as e:
                    log_console(self.console, f"⚠️ Could not delete old file: {filename} ({e})")

            else:
                log_console(self.console, f"✅ File up-to-date: {filename}")
                continue

            # Attempt download
            if download_file(download_url, filepath, self.console):
                updates_found += 1
                log_console(self.console, f"✅ Successfully updated/downloaded: {filename}")
            else:
                failed_files.append(filename)
                log_console(self.console, f"❌ Failed to update/download: {filename}")

        # 4. Final cleanup + refresh UI
        self.after(0, self._refresh_app_macros_from_local_files)
        self.after(0, self._trigger_sidebar_rebuild)

        if updates_found > 0:
            messagebox.showinfo("Update Complete", f"✅ {updates_found} file(s) successfully updated/downloaded.")
            log_console(self.console, f"Update check complete. {updates_found} file(s) updated/downloaded.")
        elif failed_files:
            messagebox.showwarning("Update Incomplete", f"⚠️ Some files failed: {', '.join(failed_files)}")
            log_console(self.console, f"Update check finished with errors: {failed_files}")
        else:
            messagebox.showinfo("All Up-to-Date", "✅ All files are already up to date!")
            log_console(self.console, "All files are already up to date.")

    # --- UTILITY COMMANDS (NEW/COMPLETED) ---
    def open_install_folder(self):
        """Opens the installation folder in the system's file explorer."""
        try:
            # Open the 2OP folder where macros are stored
            if sys.platform == "win32":
                os.startfile(INSTALL_FOLDER)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", INSTALL_FOLDER])
            else:
                subprocess.Popen(["xdg-open", INSTALL_FOLDER])
            log_console(self.console, f"Opened install folder: {INSTALL_FOLDER}")
        except Exception as e:
            log_console(self.console, f"ERROR: Failed to open folder: {e}")
            messagebox.showerror("Error", f"Could not open folder: {INSTALL_FOLDER}")

    def on_closing(self):
        """Custom handler for when the main window is closed."""
        if self._is_macro_running:
            result = messagebox.askyesno("Macro Running", "A macro is currently running. Do you want to stop it and exit the launcher?")
            if result:
                self._stop_macro()
                self.destroy()
            # If result is No, we don't destroy, and the app stays open
        else:
            self.destroy()

if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
