import pyperclip
import time

attach_string = "_window"
last_text = ""

while True:
    text = pyperclip.paste()

    # new clipboard content detected
    if text != last_text and text.strip() != "":
        modified = text + attach_string
        pyperclip.copy(modified)
        last_text = modified  # prevent infinite self-trigger
    else:
        last_text = text

    time.sleep(0.15)