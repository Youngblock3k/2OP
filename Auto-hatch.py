# -------------------------------------------------------------------------
# Auto_Hatch.py - Macro Script Template
# This file is executed by the 2OP Macro Client Launcher.
# It includes the startup messages requested by the user.
# -------------------------------------------------------------------------

# You will likely need to install the keyboard library: pip install keyboard
import keyboard
import time
import sys
import threading

# --- MACRO METADATA PRINTS (As Requested) ---
print('Auto_Hatch by Justanother_game')
print('Macro running correctly')
print('To start press F2, to stop press F3')
# -------------------------------------------

# Global state
macro_active = False
exit_flag = False

def toggle_macro(e):
    """Toggles the macro_active state when F2 is pressed."""
    global macro_active
    if e.name == 'f2':
        macro_active = True
        print("\n[STATUS] Macro Activated! Starting routine...")
    elif e.name == 'f3':
        global exit_flag
        exit_flag = True
        print("\n[STATUS] Macro Deactivated! Exiting script...")

def macro_loop():
    """The main routine that executes the macro actions."""
    global macro_active
    
    print("[INFO] Waiting for F2 to activate the macro...")
    
    while not exit_flag:
        if macro_active:
            # --- START Macro Action Loop ---
            
            # This is where your actual macro logic would go.
            # Example: Simulate an action every 0.5 seconds
            # print("Hatching action...") 
            # keyboard.press_and_release('space')
            
            # Sleep only for a very short time if the macro is running actively
            time.sleep(0.01)
            
            # --- END Macro Action Loop ---
            
        else:
            # When the macro is not active, slow down the loop to save CPU
            time.sleep(0.5)

# --- Main Execution ---

# Setup the key listeners in a non-blocking way
# This listens for F2 and F3 *globally*
keyboard.hook(toggle_macro)

try:
    # Start the macro routine in a separate thread to keep the main thread responsive
    macro_thread = threading.Thread(target=macro_loop, daemon=True)
    macro_thread.start()
    
    # Keep the main thread alive until the exit_flag is set (by pressing F3)
    while not exit_flag:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nScript interrupted manually.")

finally:
    # Ensure the script exits cleanly
    sys.exit(0)
