import TKinterModernThemes as TKMT
from TKinterModernThemes.WidgetFrame import Widget
import tkinter as tk


def buttonCMD():
        print("Button clicked!")

class App(TKMT.ThemedTKinterFrame):
    def __init__(self):
        super().__init__("2OP", "sun-valley", "dark")

        self.master.geometry("900x600")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        
        self.create_sidebar()
        
        self.content_frame = tk.Frame(self.master)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.current_page = None
        
        self.run()


    def create_sidebar(self):
        sidebar = tk.Frame(self.master, width=200, bg="#1c1c1c")
        sidebar.grid(row=0, column=0, sticky="nsw", padx=10, pady=0)
        sidebar.grid_propagate(False)
        
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
    


    def show_home(self):
         pass
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