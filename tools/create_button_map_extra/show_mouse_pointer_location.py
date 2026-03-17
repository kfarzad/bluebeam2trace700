import pyautogui
import time

try:
    while True:
        x, y = pyautogui.position()
        
        # The \r and end="" keep the print on the same line (cleans up the console)
        position_str = f"X: {str(x).rjust(4)} Y: {str(y).rjust(4)}"
        print(position_str, end="\r")
        
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nTracking stopped.")