import TKinterModernThemes as TKMT
from TKinterModernThemes.WidgetFrame import Widget
import tkinter as tk
import os
import subprocess
import threading
from tkinter import messagebox


class ScriptPanel:
    def __init__(self, parent, script_name, script_path):
        self.script_name = script_name
        self.script_path = script_path
        self.process = None
        self.running = False
        
        # Create panel frame
        self.panel = tk.Frame(parent, bg="#2c2c2c", relief="raised", bd=1)
        self.panel.pack(fill="x", pady=5, padx=5)
        
        # Script name label
        name_label = tk.Label(self.panel, text=script_name, font=("Arial", 12, "bold"),
                            bg="#2c2c2c", fg="white", anchor="w")
        name_label.pack(fill="x", padx=10, pady=(10, 5))
        
        # Status label
        self.status_label = tk.Label(self.panel, text="Status: Stopped", 
                                    font=("Arial", 10), bg="#2c2c2c", fg="gray", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=5)
        
        # Button frame
        btn_frame = tk.Frame(self.panel, bg="#2c2c2c")
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Start button
        self.start_btn = tk.Button(btn_frame, text="Start", font=("Arial", 10),
                                  bg="#28a745", fg="white", bd=0, pady=8, padx=15,
                                  activebackground="#218838", activeforeground="white",
                                  cursor="hand2", command=self.start_script)
        self.start_btn.pack(side="left", padx=(0, 5))
        
        # Stop button
        self.stop_btn = tk.Button(btn_frame, text="Stop", font=("Arial", 10),
                                 bg="#dc3545", fg="white", bd=0, pady=8, padx=15,
                                 activebackground="#c82333", activeforeground="white",
                                 cursor="hand2", command=self.stop_script, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        # Info button
        info_btn = tk.Button(btn_frame, text="Info", font=("Arial", 10),
                           bg="#17a2b8", fg="white", bd=0, pady=8, padx=15,
                           activebackground="#138496", activeforeground="white",
                           cursor="hand2", command=self.show_info)
        info_btn.pack(side="left", padx=5)
    
    def start_script(self):
        if not self.running:
            try:
                # Start script in a separate thread
                self.running = True
                self.process = subprocess.Popen(
                ['python', self.script_path],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                self.status_label.config(text="Status: Running", fg="#28a745")
                self.start_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
                
                # Monitor process in background
                threading.Thread(target=self.monitor_process, daemon=True).start()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start script:\n{str(e)}")
                self.running = False
    
    def stop_script(self):
        if self.running and self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            
            self.running = False
            self.status_label.config(text="Status: Stopped", fg="gray")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
    
    def monitor_process(self):
        if self.process:
            self.process.wait()
            if self.running:
                self.running = False
                self.status_label.config(text="Status: Completed", fg="#ffc107")
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
    
    def show_info(self):
        info = f"Script: {self.script_name}\n"
        info += f"Path: {self.script_path}\n"
        info += f"Status: {'Running' if self.running else 'Stopped'}\n"
        
        if os.path.exists(self.script_path):
            size = os.path.getsize(self.script_path)
            info += f"Size: {size} bytes"
        
        messagebox.showinfo("Script Info", info)

class App(TKMT.ThemedTKinterFrame):
    def __init__(self):
        super().__init__("2OP", "sun-valley", "dark")

        self.master.geometry("900x500")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        
        username = os.getenv('USERNAME') or os.getenv('USER')
        self.scripts_folder = f"C:/Users/{username}/2OP/scripts"
        self.script_panels = []


        self.create_sidebar()
        
        self.content_frame = tk.Frame(self.master)
        self.content_frame.grid(row=0, column=2, sticky="nsew")
        
        self.current_page = None

        self.show_home()
        
        self.run()


    def create_sidebar(self):
        sidebar = tk.Frame(self.master, width=35, bg="#1c1c1c")
        sidebar.grid(row=0, column=0, sticky="nsw", padx=(10, 0), pady=0)
        sidebar.grid_propagate(False)


        divider = tk.Frame(sidebar, width=1, bg="#3c3c3c") 
        divider.pack(side="right", fill="y", padx=(10,0))  
        
        title_label = tk.Label(sidebar, text="2OP", font=("Arial", 18, "bold"), 
                            bg="#1c1c1c", fg="white", pady=20)
        title_label.pack(fill="x")
                
        menu_items = [
            ("Home", self.show_home),
            ("Settings", self.show_settings),
            ("Social", self.show_social),
            ("Webhook", self.show_webhook),
            ("Updates", self.show_updates),
            ("Credits", self.show_credits)
        ]
        self.menu_buttons = {}
        for text, command in menu_items:
            btn = tk.Button(sidebar, text=text, font=("Arial", 12), 
                        bg="#2c2c2c", fg="white", bd=0, pady=15,
                        activebackground="#3c3c3c", activeforeground="white",
                        anchor="center", padx=0, cursor="hand2",
                        command=command, width=15)
            btn.pack(fill="x", pady=2)
            self.menu_buttons[text] = btn

        footer_label = tk.Label(sidebar, text="v1.0.0", font=("Arial", 9), 
                            bg="#1c1c1c", fg="gray", pady=10)
        footer_label.pack(side="bottom", fill="x")
    

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    

    def show_home(self):
        self.clear_content()
        self.script_panels = []
        
        
        canvas = tk.Canvas(self.content_frame, bg="#1c1c1c", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview,
                                bg="#2c2c2c", troughcolor="#1c1c1c", 
                                activebackground="#3c3c3c", bd=0)
        scrollable_frame = tk.Frame(canvas, bg="#1c1c1c")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((10, 0), window=scrollable_frame, anchor="nw")  
        canvas.configure(yscrollcommand=scrollbar.set)
        
        
        if os.path.exists(self.scripts_folder):
            scripts = [f for f in os.listdir(self.scripts_folder) 
                    if f.endswith('.py')]
            
            if scripts:
                for script in scripts:
                    script_path = os.path.join(self.scripts_folder, script)
                    panel = ScriptPanel(scrollable_frame, script, script_path)
                    self.script_panels.append(panel)
            else:
                no_scripts = tk.Label(scrollable_frame, 
                                    text="No Python scripts found in the scripts folder.",
                                    font=("Arial", 12), bg="#1c1c1c", fg="gray")
                no_scripts.pack(pady=20)
        else:
            error_label = tk.Label(scrollable_frame, 
                                text=f"Scripts folder not found:\n{self.scripts_folder}",
                                font=("Arial", 12), bg="#1c1c1c", fg="#dc3545")
            error_label.pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)  
        scrollbar.pack(side="right", fill="y")

        
    def show_settings(self):
         pass
    def show_social(self):
         pass
    
    def show_webhook(self):
         pass
    
    def show_updates(self):
         pass
    def show_credits(self):
         pass
    

if __name__ == "__main__":
    App()
