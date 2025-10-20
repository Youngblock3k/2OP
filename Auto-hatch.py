import os
import subprocess
import threading
import time
import keyboard
import tkinter as tk

# Function to create floating label
def create_label():
    label_win = tk.Toplevel()
    label_win.title("Egg Counter")
    label_win.geometry("200x50+100+100")
    label_win.attributes("-topmost", True)
    label_win.configure(bg="black")
    label_win.overrideredirect(True)

    lbl = tk.Label(label_win, text=f"Eggs Hatched: 0", fg="white", bg="black", font=("Arial", 12))
    lbl.pack(expand=True, fill="both")

    # Make draggable
    def start_move(event):
        label_win.x = event.x
        label_win.y = event.y

    def stop_move(event):
        label_win.x = None
        label_win.y = None

    def do_move(event):
        x = event.x_root - label_win.x
        y = event.y_root - label_win.y
        label_win.geometry(f"+{x}+{y}")

    lbl.bind("<Button-1>", start_move)
    lbl.bind("<ButtonRelease-1>", stop_move)
    lbl.bind("<B1-Motion>", do_move)

    return label_win, lbl

# Macro logic
def macro():
    global running, current_hatch
    label_win, lbl = create_label()

    print("\nFast Hatch n' Bubble by Justanother_Game")
    print("Macro running correctly")
    print("To start press F2, to stop press F3\n")

    while running:
        keyboard.press_and_release("e")
        keyboard.press_and_release("r")

        time.sleep(1.99)
        current_hatch += 1
        lbl.config(text=f"Eggs Hatched: {current_hatch}")

        if current_hatch >= eggs_total:
            running = False
            break

    print("\nSkript Stopped!")
    if label_win:
        label_win.destroy()

# Listener for F2/F3
def listener():
    global running
    while True:
        if keyboard.is_pressed("f2") and not running:
            running = True
            threading.Thread(target=macro, daemon=True).start()
            time.sleep(0.5)
        if keyboard.is_pressed("f3") and running:
            running = False
            time.sleep(0.5)

# Main: Open new CMD window and run script inside it
if __name__ == "__main__":
    # Open a new CMD window running this script
    if not os.environ.get("RUNNING_IN_CMD"):
        # Pass environment variable so child knows it's running in CMD
        env = os.environ.copy()
        env["RUNNING_IN_CMD"] = "1"
        subprocess.Popen(["cmd", "/k", "python", __file__], env=env)
        exit()

    # Running in new CMD
    clear = lambda: os.system("cls")
    clear()

    # Ask for eggs in CMD
    while True:
        try:
            eggs_total = int(input("HOW MANY EGG DO U HATCH: "))
            break
        except ValueError:
            print("Please enter a valid integer!")

    current_hatch = 0
    running = False

    # Start listener in thread
    threading.Thread(target=listener, daemon=True).start()

    # Start Tkinter loop for floating label
    root = tk.Tk()
    root.withdraw()  # hide main root window
    tk.mainloop()
