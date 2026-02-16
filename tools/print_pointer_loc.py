from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Clicked: ({x}, {y})")
    # To stop the listener, you could return False here
print("Tracking clicks... Press Ctrl+C in the terminal to stop.")

try:
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
except KeyboardInterrupt:
    print("\nTracking stopped.")